from pathlib import Path
import shutil
import os
import tempfile
from contextlib import contextmanager
from fastapi.staticfiles import StaticFiles

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
    def get_target_dir(self, slug):
        # Instead of outputing to a temporary directory and then
        # copying, we have repo2jupyterlite output to the end directory
        # we are serving files from.
        yield output_dir_prefix / slug

    async def upload(self, source_dir, slug):
        # In get_target_dir
        pass

    async def exists(self, slug):
        return (output_dir_prefix / slug).exists()

    async def get_redirect_url(self, slug):
        return f"/render/{slug}/index.html"

    def mount_extra_handlers(self, app):
        app.mount("/render", StaticFiles(directory=output_dir_prefix), name="render")
