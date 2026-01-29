#!/usr/bin/env python
# Copyright (c) 2026, NVIDIA CORPORATION.
"""Check that dask versions are consistent across all configuration files."""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

FILES = {
    "dependencies.yaml": REPO_ROOT / "dependencies.yaml",
    "pyproject.toml": REPO_ROOT / "pyproject.toml",
    "recipe.yaml": REPO_ROOT / "conda/recipes/rapids-dask-dependency/recipe.yaml",
}

# Patterns to extract version from each file format
# dependencies.yaml: "- dask==2026.1.1"
# pyproject.toml: '"dask==2026.1.1",'
# recipe.yaml: "- dask ==2026.1.1" (note the space before ==)
VERSION_PATTERN = re.compile(
    r"['\"]?(\w+(?:-\w+)?)\s*==\s*([0-9]+\.[0-9]+\.[0-9]+)['\"]?"
)


def extract_versions(filepath: Path) -> dict[str, str]:
    """Extract package versions from a file.

    Returns a dict mapping package name to version string.
    """
    versions = {}
    content = filepath.read_text()
    for match in VERSION_PATTERN.finditer(content):
        package = match.group(1)
        version = match.group(2)
        if package in ("dask", "dask-core", "distributed"):
            versions[package] = version
    return versions


def main() -> int:
    all_versions: dict[str, dict[str, str]] = {}

    for name, filepath in FILES.items():
        if not filepath.exists():
            print(f"ERROR: {filepath} does not exist")
            return 1
        all_versions[name] = extract_versions(filepath)

    # Collect all unique versions for each package across all files
    dask_versions: dict[str, str] = {}
    distributed_versions: dict[str, str] = {}

    for filename, versions in all_versions.items():
        if "dask" in versions:
            dask_versions[filename] = versions["dask"]
        if "dask-core" in versions:
            # dask-core should match dask version
            dask_versions[f"{filename} (dask-core)"] = versions["dask-core"]
        if "distributed" in versions:
            distributed_versions[filename] = versions["distributed"]

    errors = []

    # Check dask versions are consistent
    unique_dask = set(dask_versions.values())
    if len(unique_dask) > 1:
        errors.append("Dask version mismatch:")
        for filename, version in sorted(dask_versions.items()):
            errors.append(f"  {filename}: {version}")

    # Check distributed versions are consistent
    unique_distributed = set(distributed_versions.values())
    if len(unique_distributed) > 1:
        errors.append("Distributed version mismatch:")
        for filename, version in sorted(distributed_versions.items()):
            errors.append(f"  {filename}: {version}")

    # Check dask and distributed versions match each other
    if unique_dask and unique_distributed:
        if unique_dask != unique_distributed:
            errors.append("Dask and distributed versions should match:")
            errors.append(f"  dask versions: {unique_dask}")
            errors.append(f"  distributed versions: {unique_distributed}")

    if errors:
        print("ERROR: Dask version inconsistency detected!")
        print()
        for error in errors:
            print(error)
        print()
        print("All dask, dask-core, and distributed versions must be identical across:")
        for name, filepath in FILES.items():
            print(f"  - {filepath.relative_to(REPO_ROOT)}")
        return 1

    # Success - print summary
    version = next(iter(unique_dask)) if unique_dask else "unknown"
    print(f"Dask versions consistent: {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
