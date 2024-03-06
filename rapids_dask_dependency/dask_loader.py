# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib
import importlib.abc
import importlib.machinery
import sys
import warnings
from contextlib import contextmanager

from .patches.dask import patches as dask_patches
from .patches.distributed import patches as distributed_patches

original_warn = warnings.warn


def _warning_with_increased_stacklevel(
    message, category=None, stacklevel=1, source=None, **kwargs
):
    # Patch warnings to have the right stacklevel
    # Add 3 to the stacklevel to account for the 3 extra frames added by the loader: one
    # in this warnings function, one in the actual loader, and one in the importlib
    # call (not including all internal frames).
    original_warn(message, category, stacklevel + 3, source, **kwargs)


@contextmanager
def patch_warning_stacklevel():
    warnings.warn = _warning_with_increased_stacklevel
    yield
    warnings.warn = original_warn


class DaskLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def create_module(self, spec):
        if spec.name.startswith("dask") or spec.name.startswith("distributed"):
            with self.disable(), patch_warning_stacklevel():
                mod = importlib.import_module(spec.name)

            # Note: The spec does not make it clear whether we're guaranteed that spec
            # is not a copy of the original spec, but that is the case for now. We need
            # to assign this because the spec is used to update module attributes after
            # it is initialized by create_module.
            spec.origin = mod.__spec__.origin
            spec.submodule_search_locations = mod.__spec__.submodule_search_locations

            # TODO: I assume we'll want to only apply patches to specific submodules,
            # that'll be up to RAPIDS dask devs to decide.
            patches = dask_patches if "dask" in spec.name else distributed_patches
            for patch in patches:
                patch(mod)
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
