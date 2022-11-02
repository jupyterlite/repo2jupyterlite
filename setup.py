from setuptools import setup, find_packages

with open("README.md", encoding="utf8") as f:
    readme = f.read()

setup(
    name="repo2jupyterlite",
    version="0.2",
    install_requires=[
        "jupyterlite",
        "jupyterlab",
        "jupyterlite-xeus-python",
        "jupyter-repo2docker"
    ],
    python_requires=">=3.6",
    author="Yuvi Panda",
    author_email="yuvipanda@gmail.com",
    url="https://github.com/yuvipanda/repo2jupyterlite/",
    project_urls={
        "Source": "https://github.com/yuvipanda/repo2jupyterlite/",
        "Tracker": "https://github.com/jupyterhub/repo2docker/issues",
    },
    description="Build JupyterLite bundles from code repositories",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="3-BSD",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "repo2jupyterlite = repo2jupyterlite.app:main",
        ],
    },
)
