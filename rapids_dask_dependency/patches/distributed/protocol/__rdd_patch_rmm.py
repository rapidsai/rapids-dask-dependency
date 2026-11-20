# Vendored from distributed 2026.7.1 (BSD-3-Clause):
# https://github.com/dask/distributed/blob/2026.7.1/distributed/protocol/rmm.py
#
# The only change from upstream is that numba is no longer used: device buffers
# are copied to host with `rmm.DeviceBuffer.copy_to_host()` instead of
# `numba.cuda.as_cuda_array(...).copy_to_host()`, so that serializing CuPy/RMM
# objects works without numba installed. Remove this file (and `rmm.py` next to
# it) once distributed no longer requires numba for RMM/CuPy serialization.
from __future__ import annotations

import numpy
import rmm

from distributed.protocol.cuda import cuda_deserialize, cuda_serialize
from distributed.protocol.serialize import dask_deserialize, dask_serialize

# Used for RMM 0.11.0+ otherwise Numba serializers used
if hasattr(rmm, "DeviceBuffer"):

    @cuda_serialize.register(rmm.DeviceBuffer)
    def cuda_serialize_rmm_device_buffer(x):
        header = x.__cuda_array_interface__.copy()
        header["strides"] = (1,)
        frames = [x]
        return header, frames

    @cuda_deserialize.register(rmm.DeviceBuffer)
    def cuda_deserialize_rmm_device_buffer(header, frames):
        (arr,) = frames

        # We should already have `DeviceBuffer`
        # as RMM is used preferably for allocations
        # when it is available (as it is here).
        assert isinstance(arr, rmm.DeviceBuffer)

        return arr

    @dask_serialize.register(rmm.DeviceBuffer)
    def dask_serialize_rmm_device_buffer(x):
        header, frames = cuda_serialize_rmm_device_buffer(x)
        frames = [f.copy_to_host().data for f in frames]
        return header, frames

    @dask_deserialize.register(rmm.DeviceBuffer)
    def dask_deserialize_rmm_device_buffer(header, frames):
        (frame,) = frames

        arr = numpy.asarray(memoryview(frame))
        ptr = arr.__array_interface__["data"][0]
        size = arr.nbytes

        buf = rmm.DeviceBuffer(ptr=ptr, size=size)

        return buf
