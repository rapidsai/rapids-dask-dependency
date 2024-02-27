# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib.abc
import importlib.machinery
import sys


class DaskLoader(importlib.abc.Loader):
    def create_module(self, _) -> None:
        pass

    def exec_module(self, _):
        pass


class DaskFinder(importlib.abc.MetaPathFinder):
    def find_spec(
        self, fullname: str, _, __=None
    ) -> importlib.machinery.ModuleSpec | None:
        if fullname == "dask" or fullname.startswith("dask."):
            return importlib.machinery.ModuleSpec(
                name=fullname,
                loader=DaskLoader(),
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
