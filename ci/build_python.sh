#!/bin/bash
# Copyright (c) 2022-2023, NVIDIA CORPORATION.

set -euo pipefail

rapids-configure-conda-channels
conda config --system --remove channels rapidsai

source rapids-configure-sccache

source rapids-date-string

rapids-print-env

rapids-logger "Begin py build"

version=$(rapids-generate-version)
RAPIDS_PACKAGE_VERSION=${version} rapids-conda-retry mambabuild \
  conda/recipes/rapids-dask-dependency

rapids-upload-conda-to-s3 python
