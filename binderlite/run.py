import asyncio
import os
from pathlib import Path

from binderhub.repoproviders import (
    DataverseProvider,
    FigshareProvider,
    GistRepoProvider,
    GitHubRepoProvider,
    GitLabRepoProvider,
    GitRepoProvider,
    HydroshareProvider,
    ZenodoProvider,
)
from escapism import escape
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .publish import LocalFilesystemPublisher

HERE = Path(__file__).parent

app = FastAPI()

repo_providers = {
    "gh": GitHubRepoProvider,
    "gist": GistRepoProvider,
    "git": GitRepoProvider,
    "gl": GitLabRepoProvider,
    "zenodo": ZenodoProvider,
    "figshare": FigshareProvider,
    "hydroshare": HydroshareProvider,
    "dataverse": DataverseProvider,
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


@app.get("/build")
async def build(provider_name: str, spec: str):
    provider_class = repo_providers[provider_name]
    provider = provider_class(spec=spec)
    repo = provider.get_repo_url()
    ref = await provider.get_resolved_ref()

    # try to form this output directory deterministically, so we rebuild only
    # if necessary
    slug = escape(f"{provider_name}-{repo}-{ref}")

    if not (await publisher.exists(slug)):
        cmd = ["repo2jupyterlite", repo]
        cmd += ["--ref", ref]

        with publisher.get_target_dir(slug) as d:
            cmd += [str(d)]

            proc = await asyncio.create_subprocess_exec(*cmd)
            retcode = await proc.wait()
            if retcode != 0:
                raise HTTPException(status_code=500, detail="jupyter lite build failed")

            await publisher.upload(d, slug)
    return RedirectResponse(await publisher.get_redirect_url(slug))
