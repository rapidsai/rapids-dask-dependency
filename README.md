# Dask Metapackage

This repository provides metapackages for pip and conda that centralize the Dask version dependency across RAPIDS.
Dask's API instability means that each RAPIDS release must pin to a very specific Dask release to avoid incompatibilities.
These metapackages provide a centralized, versioned storehouse for that pinning.
The `rapids-dask-dependency` package encodes both `dask` and `distributed` requirements.

# Versioning the Metapackage Itself

This package is versioned just like the rest of RAPIDS: using CalVer, with alpha tags (trailing a\*) for nightlies.
Nightlies of the metapackage should be consumed just like nightlies of any other RAPIDS package:
  - conda packages should pin up to the minor version with a trailing `.*`, i.e. `==23.10.*`. Conda will allow nightlies to match, so no further intervention is needed.
  - pip packages should have the same pin, but wheel building scripts must add an alpha spec `>=0.0.0a0` when building nightlies to allow rapids-dask-dependency nightlies. This is the same strategy used to have RAPIDS repositories pull nightly versions of other RAPIDS dependencies (e.g. `cudf` requires `rmm` nightlies).

# Strategy for Dask Nightlies

For conda, nightlies are published to the [dask channel](https://anaconda.org/dask/).
The metapackage assumes that the `dask/label/dev` channel is included in a user's condarc so that the nightly will be found.
During RAPIDS development phase, Dask versions should be specified using PEP 440-compatible versions like `>=2023.7.1a0` so that nightlies may be picked up.
Then, at release time these versions may be pinned.


For pip, dask and distributed do not publish nightly wheels.
Therefore, the only option is for this metapackage to install those dependencies from source.
To do so, the metapackage will encode dependencies in pyproject.toml as:
```
- dask @ git+https://github.com/dask/dask.git@main
- distributed @ git+https://github.com/dask/distributed.git@main
```
At release, these dependencies will be pinned to the desired versions.
Note that encoding direct URLs as above is technically prohibited by the [Python packaging specifications](https://packaging.python.org/en/latest/specifications/version-specifiers/#direct-references).
However, while PyPI enforces this, the RAPIDS nightly index does not.
Therefore, use of this versioning strategy currently prohibits rapids-dask-dependency nightlies from being uploaded to PyPI, and they must be hosted on the RAPIDS nightly pip index.

# Patching

In addition to functioning as a metapackage, `rapids-dask-dependency` also includes code for patching dask itself.
This package is never intended to be manually imported by the user.
Instead, upon installation it installs a `.pth` file (see the [site module documentation](https://docs.python.org/3.11/library/site.html) for how these work) that will be run whenever the Python interpreter starts.
This file installs a custom [meta path loader](https://docs.python.org/3/reference/import.html#the-meta-path) that intercepts all calls to import dask modules.
This loader is set up to apply RAPIDS-specific patches to the modules, ensuring that regardless of import order issues dask modules will always be patched for RAPIDS-compatibility in environments where RAPIDS packages are installed.
