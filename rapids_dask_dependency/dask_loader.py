# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib
import importlib.abc
import importlib.machinery
import sys
from contextlib import contextmanager

from .patches.dask import patch_dask_attr
from .patches.distributed import patch_distributed_attr


class DaskFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def create_module(self, spec):
        if spec.name in ("dask", "distributed"):
            with self.disable():
                return importlib.import_module(spec.name)

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

    def find_spec(
        self, fullname: str, _, __=None
    ) -> importlib.machinery.ModuleSpec | None:
        if fullname == "dask" or fullname.startswith("dask."):
            return importlib.machinery.ModuleSpec(
                name=fullname,
                loader=self,
                # TODO: Figure out how to set the origin and loader_state correctly
                origin=None,
                loader_state=None,
                is_package=True,
            )
        if fullname == "distributed" or fullname.startswith("distributed."):
            return importlib.machinery.ModuleSpec(
                name=fullname,
                loader=self,
                # TODO: Figure out how to set the origin and loader_state correctly
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
