#!/bin/bash
# Copyright (c) 2023-2024, NVIDIA CORPORATION.

set -euo pipefail

source rapids-configure-sccache
source rapids-date-string

version=$(rapids-generate-version)

sed -i "s/^version = .*/version = \"${version}\"/g" "pyproject.toml"

python -m pip wheel . -w dist -vv --no-deps --disable-pip-version-check

RAPIDS_PY_WHEEL_NAME="rapids-dask-dependency" RAPIDS_PY_WHEEL_PURE="1" rapids-upload-wheels-to-s3 dist

# Run tests
python -m pip install $(ls dist/*.whl)[test]
python -m pytest -v tests/
