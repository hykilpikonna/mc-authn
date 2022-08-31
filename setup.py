#!/usr/bin/env python3
import pathlib

from setuptools import setup

import mc_authn

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text('utf-8')

# This call to setup() does all the work
setup(
    name="mc-authn",
    version=mc_authn.__version__,
    description="Python Authenticator for Minecraft with Microsoft",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/hykilpikonna/mc-auth",
    author="Azalea Gui",
    author_email="me@hydev.org",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=['mc_authn'],
    package_data={'mc_authn': ['mc_authn/*']},
    include_package_data=True,
    install_requires=[
        'setuptools', 'typing_extensions',
        'fastapi~=0.81.0', 'uvicorn~=0.18.3', 'ruamel.yaml', 'hypy_utils>=1.0.13'
    ],
    entry_points={
        "console_scripts": [
            "mc-authn=mc_authn:full_login",
        ]
    }
)
