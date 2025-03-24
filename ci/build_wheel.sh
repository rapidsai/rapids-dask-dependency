#!/bin/bash
# Copyright (c) 2023-2025, NVIDIA CORPORATION.

set -euo pipefail

source rapids-configure-sccache
source rapids-date-string

wheel_dir=${RAPIDS_WHEEL_BLD_OUTPUT_DIR}

version=$(rapids-generate-version)

sed -i "s/^version = .*/version = \"${version}\"/g" "pyproject.toml"

python -m pip wheel . -w "${wheel_dir}" -vv --no-deps --disable-pip-version-check

RAPIDS_PY_WHEEL_NAME="rapids-dask-dependency" RAPIDS_PY_WHEEL_PURE="1" rapids-upload-wheels-to-s3 dist

# Run tests
python -m pip install "$(echo ${wheel_dir}/*.whl)[test]"
python -m pytest -v tests/
