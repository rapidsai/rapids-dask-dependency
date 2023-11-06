# Dask Metapackage

This repository provides metapackages for pip and conda that centralize the Dask version dependency across RAPIDS.
Dask's API instability means that each RAPIDS release must pin to a very specific Dask release to avoid incompatibilities.
These metapackages provide a centralized, versioned storehouse for that pinning.
The `rapids_dask_dependency` package encodes both `dask` and `distributed` requirements.

# Metapackage Versioning

During the development cycle for RAPIDS, this metapackage will be released as an alpha-versioned package, e.g. `23.10.00a0`.

For conda packages, RAPIDS repos will only pin up to the RAPIDS patch version, i.e. `==23.10.00.*`.
When RAPIDS hits code freeze and we pin Dask versions, the package versions in this repository should be pinned.
At this time, a non-alpha release of the metapackage will be created, `23.10.00`.
This new metapackage version will be automatically picked up by other RAPIDS libraries since they will be using a `==23.10.00.*` pin.

For pip wheels, RAPIDS repos will need to set up their wheel building scripts to add an alpha spec `>=23.10.00a0` to the Dask dependencies in `pyproject.toml`.
The alpha spec addition should be conditional on whether the package is being built as a nightly or a release.
That will ensure that upon release of rapids-dask-dependency the correct version will be picked up.
This is the same strategy used to have RAPIDS repositories pull nightly versions of other RAPIDS dependencies (e.g. `cudf` requires `rmm` nightlies).

# Requiring Dask nightlies

Prior to final pinning for a release, Dask versions should be specified using PEP 440-compatible versions like `>=2023.7.1a0` so that nightlies may be picked up.
For conda, nightlies are published to the [dask channel](https://anaconda.org/dask/).
The metapackage assumes that the `dask/label/dev` channel is included in a user's condarc so that the nightly will be found.
For pip, no nightlies are published so the packages must be installed directly from source.
To do so, the metapackage will encode dependencies as:
```
- dask @ git+https://github.com/dask/dask.git@main
- distributed @ git+https://github.com/dask/distributed.git@main
```

# RAPIDS patch releases

If RAPIDS itself requires a patch release, a new metapackage version will be released that bumps the patch version e.g. `23.10.01a0`.
RAPIDS libraries should at this time update their metapackage pinnings to be `==23.10.01.*` so that metapackages corresponding to the patch release are detected.
Note that patch releases are why we must specify `==` rather than `>=` constraints.
We do not want a new metapackage release for a RAPIDS patch release to affect lower patch releases, because a patch release of RAPIDS could involve Dask changes, necessitating a bump in the Dask pinning that we do not want to propagate backwards to the previous patch release.
