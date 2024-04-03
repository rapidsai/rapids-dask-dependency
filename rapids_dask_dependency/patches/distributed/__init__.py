# Copyright (c) 2024, NVIDIA CORPORATION.

import importlib


def load_module():
    mod = importlib.import_module("distributed")
    mod._rapids_patched = True
    mod._rapids_patched = True
    return mod
