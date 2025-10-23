# Copyright (c) 2024-2025, NVIDIA CORPORATION.

import contextlib
import subprocess
from multiprocessing import Process


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
