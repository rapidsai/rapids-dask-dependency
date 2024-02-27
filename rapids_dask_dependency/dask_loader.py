# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib
import importlib.abc
import importlib.machinery
import sys
from contextlib import contextmanager

from .patches.dask import patch_dask_attr
from .patches.distributed import patch_distributed_attr


class DaskLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def create_module(self, spec):
        if spec.name in ("dask", "distributed"):
            with self.disable():
                mod = importlib.import_module(spec.name)
            spec.origin = mod.__spec__.origin
            spec.submodule_search_locations = mod.__spec__.submodule_search_locations
            return mod

    def exec_module(self, mod):
        if mod.__name__ == "dask":
            patch_dask_attr(mod)
        elif mod.__name__ == "distributed":
            patch_distributed_attr(mod)

    @contextmanager
    def disable(self):
        sys.meta_path.remove(self)
        try:
            yield
        finally:
            sys.meta_path.insert(0, self)

    def find_spec(self, fullname: str, _, __=None):
        if fullname in ("dask", "distributed") or fullname.startswith(
            "dask.") or fullname.startswith("distributed."):
            return importlib.machinery.ModuleSpec(
                name=fullname,
                loader=self,
                # Set these parameters dynamically in create_module
                origin=None,
                loader_state=None,
                is_package=True,
            )
        return None

    @classmethod
    def install(cls):
        try:
            (self,) = (obj for obj in sys.meta_path if isinstance(obj, cls))
        except ValueError:
            self = cls()
            sys.meta_path.insert(0, self)
        return self
