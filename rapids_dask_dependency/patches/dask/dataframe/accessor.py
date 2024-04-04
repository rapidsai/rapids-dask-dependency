# Copyright (c) 2024, NVIDIA CORPORATION.

from rapids_dask_dependency.importer import VendoredImporter

# TODO: Try to infer the name from the location of the file.
_importer = VendoredImporter("dask.dataframe.accessor")
load_module = _importer.load_module
