import io
import os

from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()


with open('VERSION', 'r') as f:
    __version__ = f.read().strip()

setup(
    name="mkdocs-build-plantuml-plugin",
    version=__version__,
    description="An MkDocs plugin to call plantuml locally or remote",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="mkdocs plantuml publishing documentation uml sequence diagram",
    url="https://github.com/christo-ph/mkdocs_build_plantuml",
    author="Christoph Galler",
    author_email="galler@quantor.consulting",
    license="MIT",
    python_requires=">=3.12",
    install_requires=["mkdocs>=1.0.4", "httplib2"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
    ],
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests", "example"]
    ),
    entry_points={
        "mkdocs.plugins": [
            "build_plantuml = mkdocs_build_plantuml_plugin.plantuml:BuildPlantumlPlugin"
        ]
    },
)
