# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import sys
from contextlib import contextmanager

from rapids_dask_dependency.utils import patch_warning_stacklevel, update_spec


class DaskLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self):
        # On creation and before this object is added to the meta path, cache the
        # location to the real dask if it exists so that we can use it to spoof the
        # origin of modules that we vendor instead of patching.
        self.real_dask_spec = importlib.util.find_spec("dask")

    def create_module(self, spec):
        if spec.name.startswith("dask") or spec.name.startswith("distributed"):
            with self.disable():
                try:
                    proxy = importlib.import_module(
                        f"rapids_dask_dependency.patches.{spec.name}"
                    )
                    # TODO: The warning filter will no longer work for this one, we'll
                    # have to increase the stacklevel further.
                    mod = proxy.load_module(spec)

                except ModuleNotFoundError:
                    # Add 3 to the stacklevel to account for the 3 extra frames added by
                    # the loader: one in the produced warnings function, one in the
                    # actual loader, and one in the importlib call (not including all
                    # internal frames).
                    with patch_warning_stacklevel(3):
                        mod = importlib.import_module(spec.name)

                    update_spec(spec, mod)

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
