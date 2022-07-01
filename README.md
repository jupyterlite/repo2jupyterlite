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
repo2jupyterlite https://github.com/yuvipanda/requirements requirements-build
```

You can serve the `requirements-build/` directory now statically, and it should
have the contents of the repo be present!
