from tornado.httpclient import AsyncHTTPClient, HTTPError, HTTPRequest
import json
from traitlets.config import LoggingConfigurable
import time
import os
from traitlets import Unicode, default
from datetime import timedelta
from .utils import Cache


class GitHubRepoProvider(LoggingConfigurable):
    name = Unicode("GitHub")

    # shared cache for resolved refs
    cache = Cache(1024)

    # separate cache with max age for 404 results
    # 404s don't have ETags, so we want them to expire at some point
    # to avoid caching a 404 forever since e.g. a missing repo or branch
    # may be created later
    cache_404 = Cache(1024, max_age=300)

    hostname = Unicode(
        "github.com",
        config=True,
        help="""The GitHub hostname to use

        Only necessary if not github.com,
        e.g. GitHub Enterprise.
        """,
    )

    api_base_path = Unicode(
        "https://api.{hostname}",
        config=True,
        help="""The base path of the GitHub API

        Only necessary if not github.com,
        e.g. GitHub Enterprise.

        Can use {hostname} for substitution,
        e.g. 'https://{hostname}/api/v3'
        """,
    )

    client_id = Unicode(
        config=True,
        help="""GitHub client id for authentication with the GitHub API

        For use with client_secret.
        Loaded from GITHUB_CLIENT_ID env by default.
        """,
    )

    @default("client_id")
    def _client_id_default(self):
        return os.getenv("GITHUB_CLIENT_ID", "")

    client_secret = Unicode(
        config=True,
        help="""GitHub client secret for authentication with the GitHub API

        For use with client_id.
        Loaded from GITHUB_CLIENT_SECRET env by default.
        """,
    )

    @default("client_secret")
    def _client_secret_default(self):
        return os.getenv("GITHUB_CLIENT_SECRET", "")

    access_token = Unicode(
        config=True,
        help="""GitHub access token for authentication with the GitHub API

        Loaded from GITHUB_ACCESS_TOKEN env by default.
        """,
    )

    @default("access_token")
    def _access_token_default(self):
        return os.getenv("GITHUB_ACCESS_TOKEN", "")

    @default("git_credentials")
    def _default_git_credentials(self):
        if self.access_token:
            # Based on https://github.com/blog/1270-easier-builds-and-deployments-using-git-over-https-and-oauth
            # If client_id is specified, assuming access_token is personal access token. Otherwise,
            # assume oauth basic token.
            if self.client_id:
                return r"username={client_id}\npassword={token}".format(
                    client_id=self.client_id, token=self.access_token
                )
            else:
                return rf"username={self.access_token}\npassword=x-oauth-basic"
        return ""

    @classmethod
    def from_spec_and_path(cls, spec_and_path: str):
        """
        Construct a cls with a spec + path string given.

        Spec will be consumed and whatever is leftover will be considered a
        path into the given repo.
        """
        if len(spec_and_path.split("/")) == 3:
            # Path is not specified, set it to /
            parts = spec_and_path.split("/", 3)
            parts.append("")
        else:
            parts = spec_and_path.split("/", 3)
        path = parts[3]
        return cls(parts[0], parts[1], parts[2]), path

    def __init__(self, user, repo, unresolved_ref):
        self.user = user
        self.repo = repo
        self.unresolved_ref = unresolved_ref

    async def _github_api_request(self, api_url, etag=None):
        client = AsyncHTTPClient()

        request_kwargs = {}
        if self.client_id and self.client_secret:
            request_kwargs.update(
                dict(auth_username=self.client_id, auth_password=self.client_secret)
            )

        headers = {}
        # based on: https://developer.github.com/v3/#oauth2-token-sent-in-a-header
        if self.access_token:
            headers["Authorization"] = f"token {self.access_token}"

        if etag:
            headers["If-None-Match"] = etag
        req = HTTPRequest(
            api_url, headers=headers, user_agent="BinderHub", **request_kwargs
        )

        try:
            resp = await client.fetch(req)
        except HTTPError as e:
            if e.code == 304:
                resp = e.response
            elif (
                e.code == 403
                and e.response
                and "x-ratelimit-remaining" in e.response.headers
                and e.response.headers.get("x-ratelimit-remaining") == "0"
            ):
                rate_limit = e.response.headers["x-ratelimit-limit"]
                reset_timestamp = int(e.response.headers["x-ratelimit-reset"])
                reset_seconds = int(reset_timestamp - time.time())
                self.log.error(
                    "GitHub Rate limit ({limit}) exceeded. Reset in {delta}.".format(
                        limit=rate_limit,
                        delta=timedelta(seconds=reset_seconds),
                    )
                )
                # round expiry up to nearest 5 minutes
                minutes_until_reset = 5 * (1 + (reset_seconds // 60 // 5))

                raise ValueError(
                    f"GitHub rate limit exceeded. Try again in {minutes_until_reset} minutes."
                )
            # Status 422 is returned by the API when we try and resolve a non
            # existent reference
            elif e.code in (404, 422):
                return None
            else:
                raise

        if "x-ratelimit-remaining" in resp.headers:
            # record and log github rate limit
            remaining = int(resp.headers["x-ratelimit-remaining"])
            rate_limit = int(resp.headers["x-ratelimit-limit"])
            reset_timestamp = int(resp.headers["x-ratelimit-reset"])

            # # record with prometheus
            # GITHUB_RATE_LIMIT.set(remaining)

            # log at different levels, depending on remaining fraction
            fraction = remaining / rate_limit
            if fraction < 0.2:
                log = self.log.warning
            elif fraction < 0.5:
                log = self.log.info
            else:
                log = self.log.debug

            # str(timedelta) looks like '00:32'
            delta = timedelta(seconds=int(reset_timestamp - time.time()))
            log(
                "GitHub rate limit remaining {remaining}/{limit}. Reset in {delta}.".format(
                    remaining=remaining,
                    limit=rate_limit,
                    delta=delta,
                )
            )

        return resp

    async def get_resolved_ref(self):
        if hasattr(self, "resolved_ref"):
            return self.resolved_ref

        api_url = "{api_base_path}/repos/{user}/{repo}/commits/{ref}".format(
            api_base_path=self.api_base_path.format(hostname=self.hostname),
            user=self.user,
            repo=self.repo,
            ref=self.unresolved_ref,
        )
        self.log.debug("Fetching %s", api_url)
        cached = self.cache.get(api_url)
        if cached:
            etag = cached["etag"]
            self.log.debug("Cache hit for %s: %s", api_url, etag)
        else:
            cache_404 = self.cache_404.get(api_url)
            if cache_404:
                self.log.debug("Cache hit for 404 on %s", api_url)
                return None
            etag = None

        resp = await self._github_api_request(api_url, etag=etag)
        if resp is None:
            self.log.debug("Caching 404 on %s", api_url)
            self.cache_404.set(api_url, True)
            return None
        if resp.code == 304:
            self.log.info("Using cached ref for %s: %s", api_url, cached["sha"])
            self.resolved_ref = cached["sha"]
            # refresh cache entry
            self.cache.move_to_end(api_url)
            return self.resolved_ref
        elif cached:
            self.log.debug("Cache outdated for %s", api_url)

        ref_info = json.loads(resp.body.decode("utf-8"))
        if "sha" not in ref_info:
            # TODO: Figure out if we should raise an exception instead?
            self.log.warning("No sha for %s in %s", api_url, ref_info)
            self.resolved_ref = None
            return None
        # store resolved ref and cache for later
        self.resolved_ref = ref_info["sha"]
        self.cache.set(
            api_url,
            {
                "etag": resp.headers.get("ETag"),
                "sha": self.resolved_ref,
            },
        )
        return self.resolved_ref

    async def get_resolved_spec(self):
        """
        Return a fully resolved spec.

        This can be used as the cache key
        """
        resolved_ref = await self.get_resolved_ref()
        return f"{self.user}/{self.repo}/{resolved_ref}"

    def get_resolved_repo(self):
        """
        Return a fully resolved repo
        """
        return f"https://{self.hostname}/{self.user}/{self.repo}"
