#!/bin/bash
# Copyright (c) 2023-2025, NVIDIA CORPORATION.

set -euo pipefail

source rapids-configure-sccache
source rapids-date-string
source rapids-init-pip

version=$(rapids-generate-version)

sed -i "s/^version = .*/version = \"${version}\"/g" "pyproject.toml"

python -m pip wheel . -w "${RAPIDS_WHEEL_BLD_OUTPUT_DIR}" -vv --no-deps --disable-pip-version-check

# Run tests
python -m pip install "$(echo ${RAPIDS_WHEEL_BLD_OUTPUT_DIR}/*.whl)[test]"
python -m pytest -v tests/
