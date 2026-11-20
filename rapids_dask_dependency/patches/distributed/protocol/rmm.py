# SPDX-FileCopyrightText: Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# Vendor `distributed.protocol.rmm` so that serializing `rmm.DeviceBuffer` and
# `cupy.ndarray` (whose serializers in `distributed.protocol.cupy` import from
# `distributed.protocol.rmm`) does not require numba. Upstream uses numba only to
# copy device buffers to host, which `rmm.DeviceBuffer.copy_to_host()` already
# does. RAPIDS no longer depends on numba (see
# https://github.com/rapidsai/cudf/pull/25391), so without this patch CuPy/RMM
# serialization fails in environments without numba.
#
# If rmm is not installed, importing the vendored module raises ModuleNotFoundError,
# which makes `DaskLoader` fall back to the upstream module, which in turn raises
# ImportError just like it would without this patch.
#
# This can be removed once distributed no longer requires numba for RMM/CuPy
# serialization.

from rapids_dask_dependency.loaders import make_vendored_loader

load_module = make_vendored_loader(__name__)
