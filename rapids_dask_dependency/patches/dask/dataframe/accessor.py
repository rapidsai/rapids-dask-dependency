# Copyright (c) 2024, NVIDIA CORPORATION.
import sys

# Currently vendoring this module due to https://github.com/dask/dask/pull/11035
if sys.version_info >= (3, 11, 9):
    from dask import __version__
    from packaging.version import Version

    if Version(__version__) < Version("2024.4.1"):
        from rapids_dask_dependency.loaders import make_vendored_loader

        load_module = make_vendored_loader(__name__)
