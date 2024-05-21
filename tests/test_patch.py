import contextlib
import subprocess
import tempfile
from functools import wraps
from multiprocessing import Process

import pytest


def run_test_in_subprocess(func):
    def redirect_stdout_stderr(func, stdout, stderr, *args, **kwargs):
        with open(stdout, "w") as stdout_file, open(stderr, "w") as stderr_file:
            with contextlib.redirect_stdout(stdout_file), contextlib.redirect_stderr(
                stderr_file
            ):
                func(*args, **kwargs)

    @wraps(func)
    def wrapper(*args, **kwargs):
        with tempfile.NamedTemporaryFile(
            mode="w+"
        ) as stdout, tempfile.NamedTemporaryFile(mode="w+") as stderr:
            p = Process(
                target=redirect_stdout_stderr,
                args=(func, stdout.name, stderr.name, *args),
                kwargs=kwargs,
            )
            p.start()
            p.join()
            stdout_log = stdout.file.read()
            stderr_log = stderr.file.read()
        if p.exitcode != 0:
            msg = f"Process exited {p.exitcode}."
            if stdout_log:
                msg += f"\nstdout:\n{stdout_log}"
            if stderr_log:
                msg += f"\nstderr:\n{stderr_log}"
            raise RuntimeError(msg)

    return wrapper


@run_test_in_subprocess
def test_dask():
    import dask

    assert hasattr(dask, "_rapids_patched")


@run_test_in_subprocess
def test_distributed():
    import distributed

    assert hasattr(distributed, "_rapids_patched")


@pytest.mark.parametrize("python_version", [(3, 11, 9), (3, 11, 8)])
@run_test_in_subprocess
def test_dask_accessor(python_version):
    import sys

    import dask

    # Simulate the version of Python and Dask needed to trigger vendoring of the
    # accessor module.
    sys.version_info = python_version
    dask.__version__ = "2023.4.1"

    from dask.dataframe import accessor

    assert (hasattr(accessor, "_rapids_vendored")) == (python_version >= (3, 11, 9))


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
