# Copyright (c) 2024, NVIDIA CORPORATION.

from rapids_dask_dependency.importer import VendoredImporter

_importer = VendoredImporter(__name__)
load_module = _importer.load_module
