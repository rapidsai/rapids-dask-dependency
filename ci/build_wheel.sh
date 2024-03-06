#!/bin/bash
# Copyright (c) 2023-2024, NVIDIA CORPORATION.

set -euo pipefail

source rapids-configure-sccache
source rapids-date-string

version=$(rapids-generate-version)

sed -i "s/^version = .*/version = \"${version}\"/g" "pyproject.toml"

python -m pip wheel . -w dist -vv --no-deps --disable-pip-version-check

RAPIDS_PY_WHEEL_NAME="rapids-dask-dependency" rapids-upload-wheels-to-s3 dist

# Run tests
pip install 'dist/*.whl[test]'
./conda/recipes/rapids-dask-dependency/run_test.sh
