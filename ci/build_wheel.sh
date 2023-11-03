#!/bin/bash
# Copyright (c) 2023, NVIDIA CORPORATION.

set -euo pipefail

source rapids-configure-sccache
source rapids-date-string

package_name=rapids_dask_dependency
package_dir="pip/${package_name}"
version=$(rapids-generate-version)

sed -i "s/^version = .*/version = \"${version}\"/g" "${package_dir}/pyproject.toml"

cd "${package_dir}"
python -m build . -w -vvv --no-deps --disable-pip-version-check

RAPIDS_PY_WHEEL_NAME="${package_name}" rapids-upload-wheels-to-s3 dist
