# Copyright (c) 2024, NVIDIA CORPORATION.

import warnings
from functools import lru_cache
from contextlib import contextmanager

original_warn = warnings.warn


@lru_cache()
def _make_warning_func(level):
    def _warning_with_increased_stacklevel(
        message, category=None, stacklevel=1, source=None, **kwargs
    ):
        # Patch warnings to have the right stacklevel
        original_warn(message, category, stacklevel + level, source, **kwargs)
    return _warning_with_increased_stacklevel


@contextmanager
def patch_warning_stacklevel(level):
    warnings.warn = _make_warning_func(level)
    yield
    warnings.warn = original_warn
