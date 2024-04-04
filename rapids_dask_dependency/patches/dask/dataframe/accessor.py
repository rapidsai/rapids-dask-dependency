# Copyright (c) 2024, NVIDIA CORPORATION.
import sys

if sys.version_info >= (3, 11, 9):
    from dask import __version__
    from packaging.version import Version

    if Version(__version__) < Version("2024.4.1"):
        from rapids_dask_dependency.importer import VendoredImporter

        # Currently vendoring this module due to https://github.com/dask/dask/pull/11035
        _importer = VendoredImporter(__name__)
        load_module = _importer.load_module
