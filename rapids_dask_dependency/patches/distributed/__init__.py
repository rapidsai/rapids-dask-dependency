# Copyright (c) 2024, NVIDIA CORPORATION.

from rapids_dask_dependency.importer import make_monkey_patch_loader

load_module = make_monkey_patch_loader(__name__, lambda _: None)
