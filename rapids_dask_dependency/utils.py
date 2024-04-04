# Copyright (c) 2024, NVIDIA CORPORATION.

import warnings
from contextlib import contextmanager
from functools import lru_cache

original_warn = warnings.warn


@lru_cache
def _make_warning_func(level):
    def _warning_with_increased_stacklevel(
        message, category=None, stacklevel=1, source=None, **kwargs
    ):
        # Patch warnings to have the right stacklevel
        original_warn(message, category, stacklevel + level, source, **kwargs)

    return _warning_with_increased_stacklevel


@contextmanager
def patch_warning_stacklevel(level):
    previous_warn = warnings.warn
    warnings.warn = _make_warning_func(level)
    yield
    warnings.warn = previous_warn


# Note: The Python documentation does not make it clear whether we're guaranteed that
# spec is not a copy of the original spec, but that is the case for now. We need to
# assign this because the spec is used to update module attributes after it is
# initialized by create_module.
def update_spec(spec, mod):
    spec.origin = mod.__spec__.origin
    spec.submodule_search_locations = mod.__spec__.submodule_search_locations
    return spec
