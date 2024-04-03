# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib
import importlib.abc
import importlib.machinery
import sys
from contextlib import contextmanager

from rapids_dask_dependency.utils import patch_warning_stacklevel


class DaskLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def create_module(self, spec):
        if spec.name.startswith("dask") or spec.name.startswith("distributed"):
            with self.disable():
                try:
                    proxy = importlib.import_module(f"rapids_dask_dependency.patches.{spec.name}")
                    # TODO: The warning filter will no longer work for this one, we'll
                    # have to increase the stacklevel further.
                    mod = proxy.load_module()
                except ModuleNotFoundError:
                    # Add 3 to the stacklevel to account for the 3 extra frames added by
                    # the loader: one in the produced warnings function, one in the actual
                    # loader, and one in the importlib call (not including all internal
                    # frames).
                    with patch_warning_stacklevel(3):
                        mod = importlib.import_module(spec.name)

            # Note: The spec does not make it clear whether we're guaranteed that spec
            # is not a copy of the original spec, but that is the case for now. We need
            # to assign this because the spec is used to update module attributes after
            # it is initialized by create_module.
            spec.origin = mod.__spec__.origin
            spec.submodule_search_locations = mod.__spec__.submodule_search_locations

            return mod

    def exec_module(self, _):
        pass

    @contextmanager
    def disable(self):
        sys.meta_path.remove(self)
        try:
            yield
        finally:
            sys.meta_path.insert(0, self)

    def find_spec(self, fullname: str, _, __=None):
        if (
            fullname in ("dask", "distributed")
            or fullname.startswith("dask.")
            or fullname.startswith("distributed.")
        ):
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
