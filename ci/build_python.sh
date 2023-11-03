#!/bin/bash
# Copyright (c) 2022-2023, NVIDIA CORPORATION.

set -euo pipefail

source rapids-env-update

rapids-print-env

rapids-logger "Begin py build"

version=$(rapids-generate-version)
RAPIDS_PACKAGE_VERSION=${version} rapids-conda-retry mambabuild \
  conda/recipes/rapids_dask_dependency

rapids-upload-conda-to-s3 python
