from pathlib import Path
import shutil
import os
import tempfile
from contextlib import contextmanager
from starlette.staticfiles import NotModifiedResponse, StaticFiles
from fastapi.responses import FileResponse
from email.utils import parsedate

output_dir_prefix = Path("output")
# Create the output dir if it does not exist
os.makedirs(output_dir_prefix, exist_ok=True)


class Publisher:
    @contextmanager
    def get_target_dir(self, slug):
        """
        Return the target directory repo2jupyterlite should put built files into

        The returned path is not expected to exist - although this is not
        *guaranteed* if there are multiple processes running, as slug could
        be used as a component of the generated path.

        slug is a URL-safe path component that is unique to the current
        repo being built.
        """
        # use mktmp so we know the directory is not actually created
        tmpdirname = tempfile.mktemp()
        try:
            yield tmpdirname
        finally:
            # FIXME: Make this async
            shutil.rmtree(tmpdirname)

    async def exists(self, slug):
        """
        Return true if repo represented by slug has already been published
        """
        raise NotImplementedError()

    async def upload(self, slug, source_dir):
        """
        Upload generated files for slug present in source_dir to appropriate target
        """
        raise NotImplementedError()

    async def get_redirect_url(self, slug):
        """
        Return URL to redirect users to for given built slug.

        Assumes the repo has been successfully built and published.
        """
        raise NotImplementedError()

    def mount_extra_handlers(self, app):
        """
        Mount extra FastAPI handlers in given app if needed.
        """
        pass


class LocalFilesystemPublisher(Publisher):
    @contextmanager
    def get_target_dir(self, slug):
        # Instead of outputing to a temporary directory and then
        # copying, we have repo2jupyterlite output to the end directory
        # we are serving files from.
        output_dir = output_dir_prefix / slug
        if output_dir.exists():
            shutil.rmtree(output_dir)
        yield output_dir

    async def upload(self, source_dir, slug):
        # In get_target_dir
        # Put our completion sentinel here
        with open(output_dir_prefix / slug / ".completed-sentinel", "w") as f:
            f.write("")

    async def exists(self, slug):
        return (output_dir_prefix / slug / ".completed-sentinel").exists()

    async def get_redirect_url(self, slug):
        return f"/render/{slug}/index.html"

    def is_not_modified(self, response_headers, request_headers) -> bool:
        """
        Given the request and response headers, return `True` if an HTTP
        "Not Modified" response could be returned instead.
        """
        try:
            if_none_match = request_headers["if-none-match"]
            etag = response_headers["etag"]
            if if_none_match == etag:
                return True
        except KeyError:
            pass

        try:
            if_modified_since = parsedate(request_headers["if-modified-since"])
            last_modified = parsedate(response_headers["last-modified"])
            if (
                if_modified_since is not None
                and last_modified is not None
                and if_modified_since >= last_modified
            ):
                return True
        except KeyError:
            pass

        return False

    async def serve_object(self, slug, path, request_headers):
        file_path = output_dir_prefix / slug / path
        print("serving", file_path)
        if file_path.is_dir():
            file_path = file_path / "index.html"
        # FIXME: Make this configurable, understand Cache-Control better
        resp = FileResponse(
            file_path, headers={"Cache-Control": "public, max-age=86400"}
        )
        if self.is_not_modified(resp.headers, request_headers):
            return NotModifiedResponse(resp.headers)
        return resp

    def mount_extra_handlers(self, app):
        app.mount("/render", StaticFiles(directory=output_dir_prefix), name="render")
