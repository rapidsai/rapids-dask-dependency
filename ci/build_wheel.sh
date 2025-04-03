#!/bin/bash
# Copyright (c) 2023-2025, NVIDIA CORPORATION.

set -euo pipefail

source rapids-configure-sccache
source rapids-date-string

version=$(rapids-generate-version)

sed -i "s/^version = .*/version = \"${version}\"/g" "pyproject.toml"

python -m pip wheel . -w "${RAPIDS_WHEEL_BLD_OUTPUT_DIR}" -vv --no-deps --disable-pip-version-check

RAPIDS_PY_WHEEL_NAME="rapids-dask-dependency" RAPIDS_PY_WHEEL_PURE="1" rapids-upload-wheels-to-s3 python "${RAPIDS_WHEEL_BLD_OUTPUT_DIR}"

# Run tests
python -m pip install "$(echo ${RAPIDS_WHEEL_BLD_OUTPUT_DIR}/*.whl)[test]"
python -m pytest -v tests/
