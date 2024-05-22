# Copyright (c) 2024, NVIDIA CORPORATION.

import os
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


# Default patching behavior depends on the value of the
# `RAPIDS_DASK_PATCHING` environment variable. If this
# environment variable does not exist, patching will be
# enabled. Otherwise, this variable must be set to
# `'True'` for patching to be enabled.


_env = "RAPIDS_DASK_PATCHING"


def _patching_enabled() -> bool:
    return os.environ.get(_env, "True") == "True"


@contextmanager
def patching_context(enabled: bool = True):
    original = os.environ.get(_env)
    os.environ[_env] = "True" if enabled else "False"
    try:
        yield
    finally:
        if original is None:
            os.environ.pop(_env, None)
        else:
            os.environ[_env] = "True" if original else "False"
