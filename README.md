# repo2jupyterlite

Build JupyterLite apps out of repositories.

https://github.com/jupyterlite/repo2jupyterlite/assets/591645/3a37564f-1595-4ab6-8bba-89b8429216bf

## Installation

Install from PyPI:

```bash
pip install repo2jupyterlite
```

## Build a repo with `repo2jupyterlite`

You can use the `repo2jupyterlite` command to check out any supported repo
(Git, Dataverse, Figshare, Local filestore, etc) and builds a jupyterlite
installation with `jupyter lite build`.

```bash
repo2jupyterlite https://github.com/yuvipanda/environment.yml requirements-build
```

You can serve the `requirements-build/` directory now statically, and it should
have the contents of the repo be present!

## binderlite

This repository also includes a simple web app to dynamically build and serve jupyterlite instances, similar to BinderHub UI.

### How to run

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

## Setting up a repo

`repo2jupyterlite` and `binderlite` use `jupyterlite-xeus` to install dependencies and build the JupyterLite environment.

Dependencies are specified in a `environment.yml` file. Here is an an example:

```yaml
name: xeus-python-kernel
channels:
  - https://repo.mamba.pm/emscripten-forge
  - conda-forge
dependencies:
  - xeus-python
  - numpy
  - matplotlib
  - ipycanvas
```

This file defines the `xeus-python` kernel, which enables running Python code in a JupyterLite environment. It also includes some popular Python libraries like `numpy`, `matplotlib`, and `ipycanvas`, so they are directly available in the JupyterLite environment when creating a new notebook.

Check out the documentation for more information: https://jupyterlite-xeus.readthedocs.io/en/latest/environment.html
