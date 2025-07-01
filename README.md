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

# Patching

In addition to functioning as a metapackage, `rapids-dask-dependency` also includes code for patching dask itself.
This package is never intended to be manually imported by the user.
Instead, upon installation it installs a `.pth` file (see the [site module documentation](https://docs.python.org/3.11/library/site.html) for how these work) that will be run whenever the Python interpreter starts.
This file installs a custom [meta path loader](https://docs.python.org/3/reference/import.html#the-meta-path) that intercepts all calls to import dask modules.
This loader is set up to apply RAPIDS-specific patches to the modules, ensuring that regardless of import order issues dask modules will always be patched for RAPIDS-compatibility in environments where RAPIDS packages are installed.
