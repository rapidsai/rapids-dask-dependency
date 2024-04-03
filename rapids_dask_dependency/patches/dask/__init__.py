# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib
from rapids_dask_dependency.utils import update_spec


def load_module(spec):
    mod = importlib.import_module("dask")
    update_spec(spec, mod)
    mod._rapids_patched = True
    return mod
