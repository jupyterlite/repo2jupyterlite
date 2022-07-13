import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
import asyncio
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

HERE = Path(__file__).parent

app = FastAPI()

templates = Jinja2Templates(directory=HERE / "templates")

output_dir_prefix = Path('output')
app.mount("/render", StaticFiles(directory=output_dir_prefix), name="render")
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.get("/build")
async def build(url: str, ref:str = None):
    cmd = [
        'repo2jupyterlite',
        url,
    ]
    if ref:
        cmd += ['--ref', ref]

    output_dir = str(uuid.uuid4())
    output_path = output_dir_prefix / output_dir
    cmd += [str(output_path)]

    proc = await asyncio.create_subprocess_exec(*cmd)
    retcode = await proc.wait()
    if retcode != 0:
        raise HTTPException(status_code=500, detail='jupyter lite build failed')
    return RedirectResponse(f'/render/{output_dir}/index.html')


