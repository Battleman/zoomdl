#!/usr/bin/env python3
from setuptools import setup
import os


# README as long_description
current_directory = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(current_directory, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except Exception:
    long_description = ""

setup(
    name="zoomdl",
    version="2023.01.04_homebrew",
    description="Download Zoom recorded meetings easily",
    url="https://github.com/Battleman/zoomdl",
    author="Olivier Cloux",
    license="GPL-3.0-only",
    packages=["zoomdl"],
    package_data={"zoomdl": ["zoomdl/*"]},
    include_package_data=True,
    install_requires=["demjson3~=3.0.6", "requests~=2.28.1", "tqdm~=4.64.1"],
    entry_points={
        "console_scripts": [
            "zoomdl=zoomdl:main",
        ]
    },
)
