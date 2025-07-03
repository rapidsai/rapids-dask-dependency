import importlib
import multiprocessing as mp
import subprocess
import sys
import tempfile
import os

import pytest

from dask_cuda import LocalCUDACluster

mp = mp.get_context("spawn")  # type: ignore


def _has_distributed_ucxx() -> bool:
    return bool(importlib.util.find_spec("distributed_ucxx"))


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


def _run_test_in_subprocess(test_func_name):
    """Run a test function in a subprocess and capture stdout/stderr."""
    # Use Python -c to run the test function directly
    python_code = f"""
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from tests.test_ucx import {test_func_name}
    {test_func_name}()
    print("SUCCESS", file=sys.stderr)
except Exception as e:
    print(f"ERROR: {{e}}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
    
    # Run the Python code in a subprocess
    result = subprocess.run(
        [sys.executable, "-c", python_code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    return result


@pytest.mark.parametrize("protocol", ["ucx", "ucxx", "ucx-old"])
def test_protocol(protocol):
    if protocol == "ucx":
        test_func_name = "_test_protocol_ucx"
    elif protocol == "ucxx":
        test_func_name = "_test_protocol_ucxx"
    else:
        test_func_name = "_test_protocol_ucx_old"

    result = _run_test_in_subprocess(test_func_name)
    
    # Check that the test passed
    assert result.returncode == 0, f"Test failed with return code {result.returncode}"
    assert "SUCCESS" in result.stderr, f"Test did not complete successfully. stderr: {result.stderr}"
    
    # For the ucx protocol, check if warnings are printed when distributed_ucxx is not available
    if protocol == "ucx" and not _has_distributed_ucxx():
        # Check if the warning about protocol='ucx' is printed
        combined_output = result.stdout + result.stderr
        print(combined_output)
        assert "you have requested protocol='ucx'" in combined_output, f"Expected warning not found in output: {combined_output}"
        assert "distributed-ucxx is not installed" in combined_output, f"Expected warning about distributed-ucxx not found in output: {combined_output}"
    elif protocol == "ucx" and _has_distributed_ucxx():
        # When distributed_ucxx is available, the warning should NOT be printed
        combined_output = result.stdout + result.stderr
        assert "you have requested protocol='ucx'" not in combined_output, f"Warning should not be printed when distributed_ucxx is available: {combined_output}"
    elif protocol == "ucx-old":
        # The ucx-old protocol should not generate warnings
        combined_output = result.stdout + result.stderr
        assert "you have requested protocol='ucx'" not in combined_output, f"Warning should not be printed for ucx-old protocol: {combined_output}"
