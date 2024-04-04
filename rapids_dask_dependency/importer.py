# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib
from abc import abstractmethod

from rapids_dask_dependency.utils import patch_warning_stacklevel, update_spec


class BaseImporter:
    @abstractmethod
    def load_module(self, spec):
        pass


# TODO: Support an actual patch function.
class MonkeyPatchImporter(BaseImporter):
    """The base importer for modules that are monkey-patched."""

    def __init__(self, name):
        self.name = name

    def load_module(self, spec):
        # Four extra stack frames: 1) DaskLoader.create_module, 2)
        # MonkeyPatchImporter.load_module, 3) importlib.import_module, and 4) the
        # patched warnings function (not including the internal frames, which warnings
        # ignores).
        with patch_warning_stacklevel(4):
            mod = importlib.import_module(self.name)
        update_spec(spec, mod)
        mod._rapids_patched = True
        return mod


class VendoredImporter(BaseImporter):
    """The base importer for vendored modules."""

    # Vendored files use a standard prefix to avoid name collisions.
    default_prefix = "__rdd_patch_"

    def __init__(self, module):
        self.real_module = module
        module_parts = module.split(".")
        module_parts[-1] = self.default_prefix + module_parts[-1]
        self.vendored_module = ".".join(module_parts)

    def load_module(self, spec):
        vendored_module = importlib.import_module(
            f"rapids_dask_dependency.patches.{self.vendored_module}"
        )
        # TODO: Need a way to get this cleanly when the loader is already installed.
        # update_spec(spec, mod)
        return vendored_module
