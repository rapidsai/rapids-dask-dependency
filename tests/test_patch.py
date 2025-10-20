# Copyright (c) 2024-2025, NVIDIA CORPORATION.

import multiprocessing
import subprocess


def _run_in_subprocess(func):
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=func, args=(q,))
    p.start()
    result = q.get()
    p.join()
    return result


def check_dask(q: multiprocessing.Queue):
    import dask

    q.put(hasattr(dask, "_rapids_patched"))


def test_dask():
    result = _run_in_subprocess(check_dask)
    assert result


def check_distributed(q: multiprocessing.Queue):
    import distributed

    result = hasattr(distributed, "_rapids_patched")
    q.put(result)


def test_distributed():
    result = _run_in_subprocess(check_distributed)
    assert result


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
