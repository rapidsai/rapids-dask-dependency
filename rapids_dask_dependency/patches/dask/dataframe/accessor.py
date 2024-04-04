# Copyright (c) 2024, NVIDIA CORPORATION.

from rapids_dask_dependency.importer import VendoredImporter

# Currently vendoring this module due to https://github.com/dask/dask/pull/11035
_importer = VendoredImporter(__name__)
load_module = _importer.load_module
