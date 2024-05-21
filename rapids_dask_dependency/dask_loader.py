# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import sys
from contextlib import contextmanager

from rapids_dask_dependency.utils import patch_warning_stacklevel


class DaskLoader(importlib.machinery.SourceFileLoader):
    def __init__(self, fullname, path, finder):
        super().__init__(fullname, path)
        self._finder = finder

    def create_module(self, spec):
        with self._finder.disable(spec.name):
            try:
                # Absolute import is important here to avoid shadowing the real dask
                # and distributed modules in sys.modules. Bad things will happen if
                # we use relative imports here.
                proxy = importlib.import_module(
                    f"rapids_dask_dependency.patches.{spec.name}"
                )
                if hasattr(proxy, "load_module"):
                    return proxy.load_module()
            except ModuleNotFoundError:
                pass

            # Three extra stack frames: 1) DaskLoader.create_module,
            # 2) importlib.import_module, and 3) the patched warnings function (not
            # including the internal frames, which warnings ignores).
            with patch_warning_stacklevel(3):
                return importlib.import_module(spec.name)

    def exec_module(self, _):
        pass


class DaskFinder(importlib.abc.MetaPathFinder):
    def __init__(self):
        self._blocklist = set()

    @contextmanager
    def disable(self, name):
        # This is a context manager that prevents this finder from intercepting calls to
        # import a specific name. We must do this to avoid infinite recursion when
        # calling import_module in create_module. However, we cannot blanket disable the
        # finder because that causes it to be bypassed when transitive imports occur
        # within import_module.
        try:
            self._blocklist.add(name)
            yield
        finally:
            self._blocklist.remove(name)

    def find_spec(self, fullname: str, _, __=None):
        if fullname in self._blocklist:
            return None
        if (
            fullname in ("dask", "distributed")
            or fullname.startswith("dask.")
            or fullname.startswith("distributed.")
        ):
            with self.disable(fullname):
                if (real_spec := importlib.util.find_spec(fullname)) is None:
                    return None
            spec = importlib.machinery.ModuleSpec(
                name=fullname,
                loader=DaskLoader(fullname, real_spec.origin, self),
                origin=real_spec.origin,
                loader_state=real_spec.loader_state,
                is_package=real_spec.submodule_search_locations is not None,
            )
            spec.submodule_search_locations = real_spec.submodule_search_locations
            return spec
        return None

    @classmethod
    def install(cls):
        try:
            (self,) = (obj for obj in sys.meta_path if isinstance(obj, cls))
        except ValueError:
            self = cls()
            sys.meta_path.insert(0, self)
        return self
