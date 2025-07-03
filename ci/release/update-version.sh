#!/usr/bin/env bash
# Copyright (c) 2023-2025, NVIDIA CORPORATION.

## Usage
# bash update-version.sh <new_version>

# Format is YY.MM.PP - no leading 'v' or trailing 'a'
NEXT_FULL_TAG=$1

# Get current version
CURRENT_TAG=$(git tag --merged HEAD | grep -xE '^v.*' | sort --version-sort | tail -n 1 | tr -d 'v')

# Get <major>.<minor> for next version
NEXT_MAJOR=$(echo "$NEXT_FULL_TAG" | awk '{split($0, a, "."); print a[1]}')
NEXT_MINOR=$(echo "$NEXT_FULL_TAG" | awk '{split($0, a, "."); print a[2]}')
NEXT_PATCH=$(echo "$NEXT_FULL_TAG" | awk '{split($0, a, "."); print a[3]}')
NEXT_SHORT_TAG=${NEXT_MAJOR}.${NEXT_MINOR}
NEXT_FULL_TAG=${NEXT_MAJOR}.${NEXT_MINOR}.${NEXT_PATCH}
NEXT_UCXPY_VERSION="$(curl -s https://version.gpuci.io/rapids/"${NEXT_SHORT_TAG}")"

# Need to distutils-normalize the versions for some use cases
NEXT_RAPIDS_SHORT_TAG_PEP440=$(python -c "from packaging.version import Version; print(Version('${NEXT_SHORT_TAG}'))")
echo "Next tag is ${NEXT_RAPIDS_SHORT_TAG_PEP440}"

echo "Preparing release $CURRENT_TAG => $NEXT_FULL_TAG"

# Inplace sed replace; workaround for Linux and Mac
function sed_runner() {
  sed -i.bak ''"$1"'' $2 && rm -f ${2}.bak
}

sed_runner "s/^version = .*/version = \"${NEXT_FULL_TAG}a0\"/" pyproject.toml

for FILE in .github/workflows/*.yaml; do
  sed_runner "/shared-workflows/ s/@.*/@branch-${NEXT_SHORT_TAG}/g" "${FILE}"
done

DEPENDENCIES=(
  dask-cuda
)
UCXX_DEPENDENCIES=(
  distributed-ucxx
  ucx-py
)
for FILE in conda/recipes/*/recipe.yaml; do
  for DEP in "${DEPENDENCIES[@]}"; do
    sed_runner "s/^\([[:space:]]*-[[:space:]]*${DEP} ==\).*/\1${NEXT_RAPIDS_SHORT_TAG_PEP440}.*/" conda/recipes/rapids-dask-dependency/recipe.yaml
  done
  for DEP in "${UCXX_DEPENDENCIES[@]}"; do
    sleep 0
    sed_runner "s/^\([[:space:]]*-[[:space:]]*${DEP} ==\).*/\1${NEXT_UCXPY_VERSION}.*/" conda/recipes/rapids-dask-dependency/recipe.yaml
  done
done

for DEP in "${DEPENDENCIES[@]}"; do
  sed_runner "/\"${DEP}\(-cu[[:digit:]]\{2\}\)\{0,1\}==/ s/==.*\"/==${NEXT_RAPIDS_SHORT_TAG_PEP440}\.*,>=0.0.0a0\"/g" "pyproject.toml"
done
for DEP in "${UCXX_DEPENDENCIES[@]}"; do
  sed_runner "/\"${DEP}\(-cu[[:digit:]]\{2\}\)\{0,1\}==/ s/==.*\"/==${NEXT_UCXPY_VERSION}\.*,>=0.0.0a0\"/g" "pyproject.toml"
done
