# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib

from rapids_dask_dependency.utils import patch_warning_stacklevel, update_spec


class MonkeyPatchImporter:
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
