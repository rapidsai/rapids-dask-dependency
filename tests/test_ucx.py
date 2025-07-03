import importlib
import multiprocessing as mp

import pytest

from dask_cuda import LocalCUDACluster

mp = mp.get_context("spawn")  # type: ignore


def _has_distributed_ucxx() -> bool:
    bool(importlib.util.find_spec("distributed_ucxx"))


def _test_protocol_ucx():
    with LocalCUDACluster(protocol="ucx") as cluster:
        assert cluster.scheduler_comm.address.startswith("ucx://")

        if _has_distributed_ucxx():
            assert all(
                isinstance(batched_send.comm, distributed_ucxx.ucxx.UCXX)
                for batched_send in cluster.scheduler.stream_comms.values()
            )
        else:
            import rapids_dask_dependency

            # with pytest.warns(UserWarning, match="you have requested protocol='ucx'"):
            assert all(
                isinstance(
                    batched_send.comm,
                    rapids_dask_dependency.patches.distributed.comm.__rdd_patch_ucx.UCX,
                )
                for batched_send in cluster.scheduler.stream_comms.values()
            )


def _test_protocol_ucxx():
    if _has_distributed_ucxx():
        with LocalCUDACluster(protocol="ucxx") as cluster:
            assert cluster.scheduler_comm.address.startswith("ucxx://")
            assert all(
                isinstance(batched_send.comm, distributed_ucxx.ucxx.UCXX)
                for batched_send in cluster.scheduler.stream_comms.values()
            )
    else:
        with pytest.raises(RuntimeError, match="Cluster failed to start"):
            LocalCUDACluster(protocol="ucxx")


def _test_protocol_ucx_old():
    with LocalCUDACluster(protocol="ucx-old") as cluster:
        assert cluster.scheduler_comm.address.startswith("ucx-old://")

        import rapids_dask_dependency

        assert all(
            isinstance(
                batched_send.comm,
                rapids_dask_dependency.patches.distributed.comm.__rdd_patch_ucx.UCX,
            )
            for batched_send in cluster.scheduler.stream_comms.values()
        )


@pytest.mark.parametrize("protocol", ["ucx", "ucxx", "ucx-old"])
def test_protocol(protocol):
    if protocol == "ucx":
        p = mp.Process(target=_test_protocol_ucx)
    elif protocol == "ucxx":
        p = mp.Process(target=_test_protocol_ucxx)
    else:
        p = mp.Process(target=_test_protocol_ucx_old)

    p.start()
    p.join(timeout=60)

    if p.is_alive():
        p.kill()
        p.close()

    assert p.exitcode == 0
