# repo2jupyterlite

Build jupyterlite apps out of repositories

## Installation

Install from PyPI:

```bash
pip install repo2jupyterlite
```

## Build a repo

You can use the `repo2jupyterlite` command to check out any supported repo
(Git, Dataverse, Figshare, Local filestore, etc) and builds a jupyterlite
installation with `jupyter lite build`.

```bash
repo2jupyterlite https://github.com/yuvipandas/environment.yml requirements-build
```

You can serve the `requirements-build/` directory now statically, and it should
have the contents of the repo be present!

# binderlite

A simple web app to dynamically build and serve jupyterlite instances.

## How to run

1. Create a new conda env with required dependencies

   ```
   mamba env create -n binderlite -f environment.yml
   ```

2. Install repo2jupyterlite from this repo

   ```bash
   pip install -e .
   ```

3. Use `uvicorn` to run the web app

   ```bash
   uvicorn binderlite.run:app
   ```
