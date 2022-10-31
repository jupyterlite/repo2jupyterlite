from repo2docker import contentproviders
import argparse
import logging
import shutil
import sys
import subprocess
import os
import tempfile

# List of ContentProviders to use
content_providers = [
    contentproviders.Local,
    contentproviders.Zenodo,
    contentproviders.Figshare,
    contentproviders.Dataverse,
    contentproviders.Hydroshare,
    contentproviders.Swhid,
    contentproviders.Mercurial,
    contentproviders.Git,
]

logging.basicConfig(format='%(asctime)s %(msg)s', level=logging.DEBUG)
log = logging


def fetch(url, ref, checkout_path):
    """
    Fetch repo from url at ref, and check it out to checkout_path

    Uses repo2docker to detect what kinda url is going to be checked out,
    and fetches it into checkout_path.

    checkout_path should be empty.
    """
    picked_content_provider = None
    for ContentProvider in content_providers:
        cp = ContentProvider()
        spec = cp.detect(url, ref=ref)
        if spec is not None:
            picked_content_provider = cp
            log.info(
                "Picked {cp} content "
                "provider.\n".format(cp=cp.__class__.__name__)
            )
            break

    if picked_content_provider is None:
        log.error(
            "No matching content provider found for " "{url}.".format(url=url)
        )
        # FIXME: How to handle this?
        return


    for log_line in picked_content_provider.fetch(
        spec, checkout_path, yield_output=True
    ):
        log.info(log_line, extra=dict(phase="fetching"))

def build(repo_dir, output_dir):
    """
    Build a JupyterLite distribution.

    Builds it out of repo_dir, outputs contents to output_dir.

    jupyterlite_config.json is read from base of repo if it exists.
    """
    abs_output_path = os.path.abspath(output_dir)
    cmd = [
        'jupyter', 'lite', 'build', '.', '--output-dir', abs_output_path, '--contents', '.',
    ]
    if os.path.exists(os.path.join(repo_dir, 'jupyterlite_config.json')):
        cmd += ['--config', 'jupyterlite_config.json']
    subprocess.check_call(cmd, cwd=repo_dir)

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        'url',
        help="URL to repo to build"
    )
    argparser.add_argument(
        'output_dir',
        help='Path to output built JupyterLite distribution to'
    )
    argparser.add_argument(
        '--ref',
        default=None,
        help="Ref to check out of the repo to build"
    )

    args = argparser.parse_args()

    if os.path.exists(args.output_dir):
        print(f"Output path ${args.output_dir} already exists, aborting...")
        sys.exit(1)

    if os.path.exists(args.url):
        # Trying to build a local path, so no fetching is necessary
        cleanup_after = False
        checkout_dir = args.url
    else:
        cleanup_after = True
        checkout_dir = tempfile.gettempdir()
        fetch(args.url, args.ref, checkout_dir)

    try:
        build(checkout_dir, args.output_dir)
        print(f"Go to http://localhost:8000/{args.output_dir}")
    finally:
        if cleanup_after:
            shutil.rmtree(checkout_dir)
