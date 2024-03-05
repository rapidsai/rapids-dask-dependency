#!/bin/bash
# Copyright (c) 2023, NVIDIA CORPORATION.

set -euo pipefail

source rapids-configure-sccache
source rapids-date-string

package_name=rapids-dask-dependency
package_dir="pip/${package_name}"
version=$(rapids-generate-version)

sed -i "s/^version = .*/version = \"${version}\"/g" "${package_dir}/pyproject.toml"

cd "${package_dir}"
python -m pip wheel . -w dist -vvv --no-deps --disable-pip-version-check

RAPIDS_PY_WHEEL_NAME="${package_name}" RAPIDS_PY_WHEEL_PURE="1" rapids-upload-wheels-to-s3 dist
