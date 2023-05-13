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


app.mount("/render", StaticFiles(directory=output_dir_prefix), name="render")
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "repo_providers": repo_providers}
    )


@app.get("/build")
async def build(provider: str, spec: str):
    provider_class = repo_providers[provider]
    provider = provider_class(spec=spec)
    repo = provider.get_repo_url()
    ref = await provider.get_resolved_ref()

    # try to form this output directory deterministically, so we rebuild only
    # if necessary
    output_dir = escape(f"{provider}-{repo}-{ref}")
    output_path = output_dir_prefix / output_dir

    if not output_path.exists():
        cmd = ["repo2jupyterlite", repo]
        cmd += ["--ref", ref]

        cmd += [str(output_path)]

        proc = await asyncio.create_subprocess_exec(*cmd)
        retcode = await proc.wait()
        if retcode != 0:
            raise HTTPException(status_code=500, detail="jupyter lite build failed")
    return RedirectResponse(f"/render/{output_dir}/index.html")
