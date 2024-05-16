# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib
import importlib.util
from abc import abstractmethod

from rapids_dask_dependency.utils import patch_warning_stacklevel


class BaseImporter:
    @abstractmethod
    def load_module(self):
        pass


class MonkeyPatchImporter(BaseImporter):
    """The base importer for modules that are monkey-patched."""

    def __init__(self, name, patch_func):
        self.name = name.replace("rapids_dask_dependency.patches.", "")
        self.patch_func = patch_func

    def load_module(self):
        # Four extra stack frames: 1) DaskLoader.create_module, 2)
        # MonkeyPatchImporter.load_module, 3) importlib.import_module, and 4) the
        # patched warnings function (not including the internal frames, which warnings
        # ignores).
        with patch_warning_stacklevel(4):
            mod = importlib.import_module(self.name)
        self.patch_func(mod)
        mod._rapids_patched = True
        return mod


class VendoredImporter(BaseImporter):
    """The base importer for vendored modules."""

    # Vendored files use a standard prefix to avoid name collisions.
    default_prefix = "__rdd_patch_"

    def __init__(self, module):
        self.real_module_name = module.replace("rapids_dask_dependency.patches.", "")
        module_parts = module.split(".")
        module_parts[-1] = self.default_prefix + module_parts[-1]
        self.vendored_module_name = ".".join(module_parts)

    def load_module(self):
        return importlib.import_module(self.vendored_module_name)
