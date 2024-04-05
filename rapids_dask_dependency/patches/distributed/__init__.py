# Copyright (c) 2024, NVIDIA CORPORATION.

from rapids_dask_dependency.importer import MonkeyPatchImporter

_importer = MonkeyPatchImporter(__name__, lambda _: None)
load_module = _importer.load_module
