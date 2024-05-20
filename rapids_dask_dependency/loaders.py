# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib
import importlib.util

from rapids_dask_dependency.utils import patch_warning_stacklevel

# Vendored files use a standard prefix to avoid name collisions.
DEFAULT_VENDORED_PREFIX = "__rdd_patch_"


def make_monkey_patch_loader(name, patch_func):
    """Create a loader for monkey-patched modules."""

    def load_module():
        # Four extra stack frames: 1) DaskLoader.create_module, 2)
        # load_module, 3) importlib.import_module, and 4) the patched warnings function.
        with patch_warning_stacklevel(4):
            mod = importlib.import_module(
                name.replace("rapids_dask_dependency.patches.", "")
            )
        patch_func(mod)
        mod._rapids_patched = True
        return mod

    return load_module


def make_vendored_loader(name):
    """Create a loader for vendored modules."""

    def load_module():
        parts = name.split(".")
        parts[-1] = DEFAULT_VENDORED_PREFIX + parts[-1]
        mod = importlib.import_module(".".join(parts))
        mod._rapids_vendored = True
        return mod

    return load_module
