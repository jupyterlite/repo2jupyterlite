import asyncio
import os
from pathlib import Path
import string


from repoproviders.github import GitHubRepoProvider
from escapism import escape
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import (
    Response,
    HTMLResponse,
    RedirectResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .publish import LocalFilesystemPublisher

HERE = Path(__file__).parent

app = FastAPI()

repo_providers = {
    "gh": GitHubRepoProvider,
}

templates = Jinja2Templates(directory=HERE / "templates")

output_dir_prefix = Path("output")
# Create the output dir if it does not exist
os.makedirs(output_dir_prefix, exist_ok=True)


app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")


publisher = LocalFilesystemPublisher()
publisher.mount_extra_handlers(app)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "repo_providers": repo_providers}
    )


@app.get("/v1/{provider_name:str}/{spec_and_path:path}")
async def render(provider_name: str, spec_and_path: str, request: Request):
    provider_class = repo_providers[provider_name]

    provider, path = provider_class.from_spec_and_path(spec_and_path)
    if path.strip() == "":
        # If there's no path component, redirect until there is!
        # This allows for easy copy pasting
        return RedirectResponse(str(request.url).rstrip("/") + "/lab/index.html")

    ref = await provider.get_resolved_ref()

    if ref != provider.unresolved_ref:
        # Ref was resolved! Let's redirect to resolved ref
        return RedirectResponse(
            f"/v1/{provider_name}/{await provider.get_resolved_spec()}/{path}"
        )

    resolved_spec = await provider.get_resolved_spec()

    # Explicitly allow "-" and "/", so these output folders nest. Without
    # this, you will end up with one huge folder with millions of outputs,
    # which is a perf nightmare
    slug = escape(
        f"{provider_name}-{resolved_spec}",
        safe=string.ascii_letters + string.digits + "-" + "/",
    )

    if not (await publisher.exists(slug)):
        # We only trigger builds for files ending with .html, to avoid triggering
        # a ton of builds when we are recovering from partial cache evictions -
        # each JS and CSS thing will trigger its own build!
        if path.endswith(".html"):
            cmd = ["repo2jupyterlite", provider.get_resolved_repo()]
            cmd += ["--ref", ref]

            with publisher.get_target_dir(slug) as d:
                cmd += [str(d)]

                print(cmd)
                proc = await asyncio.create_subprocess_exec(*cmd)
                retcode = await proc.wait()
                if retcode != 0:
                    raise HTTPException(
                        status_code=500, detail="jupyter lite build failed"
                    )

                await publisher.upload(d, slug)
        else:
            return Response(status_code=404)
    # FIXME: This means we don't support etags, etc.
    # But we can and should rely on downstream proxy to support those!
    return await publisher.serve_object(slug, path, request.headers)
