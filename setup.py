# Copyright (c) 2024, NVIDIA CORPORATION.
import os

from setuptools import setup
from setuptools.command.build_py import build_py

# Adapted from https://stackoverflow.com/a/71137790
class build_py_with_pth_file(build_py):
     """Include the .pth file in the generated wheel."""
     def run(self):
         super().run()

         fn = "_rapids_dask_dependency.pth"

         outfile = os.path.join(self.build_lib, fn)
         self.copy_file(fn, outfile, preserve_mode=0)

setup(cmdclass={"build_py": build_py_with_pth_file})
