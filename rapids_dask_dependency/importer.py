# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib
import importlib.util
from abc import abstractmethod

from rapids_dask_dependency.utils import patch_warning_stacklevel, update_spec


class BaseImporter:
    @abstractmethod
    def load_module(self, spec):
        pass


class MonkeyPatchImporter(BaseImporter):
    """The base importer for modules that are monkey-patched."""

    def __init__(self, name, patch_func):
        self.name = name.replace("rapids_dask_dependency.patches.", "")
        self.patch_func = patch_func

    def load_module(self, spec):
        # Four extra stack frames: 1) DaskLoader.create_module, 2)
        # MonkeyPatchImporter.load_module, 3) importlib.import_module, and 4) the
        # patched warnings function (not including the internal frames, which warnings
        # ignores).
        with patch_warning_stacklevel(4):
            mod = importlib.import_module(self.name)
        self.patch_func(mod)
        update_spec(spec, mod.__spec__)
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

    def load_module(self, spec):
        vendored_module = importlib.import_module(self.vendored_module_name)
        # At this stage the module loader must have been disabled for this module, so we
        # can access the original module. We don't want to actually import it, we just
        # want enough information on it to update the spec.
        original_spec = importlib.util.find_spec(self.real_module_name)
        update_spec(spec, original_spec)
        return vendored_module
