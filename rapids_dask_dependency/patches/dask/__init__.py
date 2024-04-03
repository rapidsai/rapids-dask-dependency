# Copyright (c) 2024, NVIDIA CORPORATION.

from rapids_dask_dependency.importer import MonkeyPatchImporter

_importer = MonkeyPatchImporter("dask")
load_module = _importer.load_module
