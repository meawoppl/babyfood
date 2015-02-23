#!/usr/bin/env python
# Get the version number from git tags:
# Fetch version from git tags, and write to version.py.
# Also, when git is not available (PyPi package), use stored version.py.
import os, subprocess
from distutils.core import setup

versionFileName = os.path.join(os.path.dirname(__file__), "babyfood", '_version.py')
version_git = subprocess.check_output(["git", "describe", "--long", "--tags"]).decode("ascii").rstrip()
vn, build, shortHash = version_git.split("-")

version_msg = "# Do not edit or commit this file, pipeline versioning is governed by git tags"
quoted = lambda s: '"' + s + '"'

with open(versionFileName, 'w') as fh:
    fh.write(version_msg + os.linesep)
    fh.write("__version__ = " + quoted(vn) + os.linesep)
    fh.write("__build__ = " + quoted(build) + os.linesep)
    fh.write("__githash__ = " + quoted(shortHash) + os.linesep)

setup(name='babyfood',
      version=vn,
      description='PCB Tools',
      author='Matthew Goodman',
      author_email='meawoppl@gmail.com',
      url='https://www.github.com/babyfood',
      packages=["babyfood",
                "babyfood.components",
                "babyfood.features",
                "babyfood.io",
                "babyfood.layers",
                "babyfood.pcb",
                "babyfood.tests"]
      )
