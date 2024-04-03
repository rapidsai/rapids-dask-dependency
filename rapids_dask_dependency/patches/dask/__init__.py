# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib


def load_module():
    mod = importlib.import_module("dask")
    mod._rapids_patched = True
    return mod
