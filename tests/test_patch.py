# Copyright (c) 2024-2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

import contextlib
import subprocess
import sys
import textwrap
from multiprocessing import Process

import pytest


def redirect_stdout_stderr(func, stdout, stderr, *args, **kwargs):
    with open(stdout, "w") as stdout_file, open(stderr, "w") as stderr_file:
        with (
            contextlib.redirect_stdout(stdout_file),
            contextlib.redirect_stderr(stderr_file),
        ):
            func(*args, **kwargs)


def run_test_in_subprocess(func, tmp_path, *args, **kwargs):
    stdout = tmp_path / "stdout.log"
    stderr = tmp_path / "stderr.log"
    p = Process(
        target=redirect_stdout_stderr,
        args=(func, stdout, stderr, *args),
        kwargs=kwargs,
    )
    p.start()
    p.join()
    stdout_log = stdout.read_text()
    stderr_log = stderr.read_text()
    if p.exitcode != 0:
        msg = f"Process exited {p.exitcode}."
        if stdout_log:
            msg += f"\nstdout:\n{stdout_log}"
        if stderr_log:
            msg += f"\nstderr:\n{stderr_log}"
        raise RuntimeError(msg)


def check_dask():
    import dask

    assert hasattr(dask, "_rapids_patched")


def test_dask(tmp_path):
    run_test_in_subprocess(check_dask, tmp_path)


def check_distributed():
    import distributed

    assert hasattr(distributed, "_rapids_patched")


def test_distributed(tmp_path):
    run_test_in_subprocess(check_distributed, tmp_path)


def test_dask_cli():
    try:
        subprocess.run(["dask", "--help"], capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        print(e.stdout.decode())
        print(e.stderr.decode())
        raise


def test_dask_as_module():
    try:
        subprocess.run(
            ["python", "-m", "dask", "--help"], capture_output=True, check=True
        )
    except subprocess.CalledProcessError as e:
        print(e.stdout.decode())
        print(e.stderr.decode())
        raise


def test_distributed_cli_dask_spec_as_module():
    try:
        subprocess.run(
            ["python", "-m", "distributed.cli.dask_spec", "--help"],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(e.stdout.decode())
        print(e.stderr.decode())
        raise


def run_python_in_subprocess(code):
    """Run code in a fresh interpreter so that no modules leak in from other tests."""
    try:
        subprocess.run(
            [sys.executable, "-c", textwrap.dedent(code)],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(e.stdout.decode())
        print(e.stderr.decode())
        raise


def test_distributed_protocol_rmm_vendored():
    pytest.importorskip("rmm")
    run_python_in_subprocess(
        """
        import sys

        # Make any attempt to import numba fail.
        sys.modules["numba"] = None

        import distributed.protocol.rmm

        assert hasattr(distributed.protocol.rmm, "_rapids_vendored")
        assert hasattr(
            distributed.protocol.rmm, "dask_deserialize_rmm_device_buffer"
        )
        """
    )


def test_distributed_protocol_rmm_without_rmm():
    # Without rmm, importing `distributed.protocol.rmm` must still raise ImportError
    # like upstream does, so that e.g. `distributed.protocol.cupy` falls back.
    run_python_in_subprocess(
        """
        import sys
        import warnings

        sys.modules["rmm"] = None

        try:
            # Without rmm we fall back to the upstream module, which imports numba
            # first if it is installed. Ignore any warnings numba may emit on
            # import, they are irrelevant for this test.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import distributed.protocol.rmm  # noqa: F401
        except ImportError:
            pass
        else:
            raise AssertionError("ImportError not raised")
        """
    )


def test_distributed_protocol_rmm_cupy_serialize():
    cupy = pytest.importorskip("cupy")
    pytest.importorskip("rmm")
    try:
        if cupy.cuda.runtime.getDeviceCount() == 0:
            pytest.skip("No GPU available")
    except cupy.cuda.runtime.CUDARuntimeError:
        pytest.skip("No GPU available")

    run_python_in_subprocess(
        """
        import sys

        import cupy
        import rmm

        from distributed.protocol import deserialize, serialize

        objs = [
            cupy.arange(10),
            # Non-contiguous
            cupy.arange(12.0).reshape(3, 4)[:, ::2],
            rmm.DeviceBuffer.to_device(b"abcdef"),
        ]
        for x in objs:
            for serializers in (["cuda"], ["dask"]):
                header, frames = serialize(
                    x, serializers=serializers, on_error="raise"
                )
                y = deserialize(header, frames, deserializers=serializers)
                assert type(y) is type(x)
                if isinstance(x, rmm.DeviceBuffer):
                    assert y.tobytes() == x.tobytes()
                else:
                    assert y.shape == x.shape
                    assert y.dtype == x.dtype
                    assert (cupy.asnumpy(y) == cupy.asnumpy(x)).all()

        assert hasattr(sys.modules["distributed.protocol.rmm"], "_rapids_vendored")
        assert "numba" not in sys.modules
        """
    )
