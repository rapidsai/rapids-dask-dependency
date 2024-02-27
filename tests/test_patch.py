from functools import wraps
from multiprocessing import Process


def run_test_in_subprocess(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        p = Process(target=func, args=args, kwargs=kwargs)
        p.start()
        p.join()

    return wrapper


@run_test_in_subprocess
def test_dask():
    import dask

    assert hasattr(dask, "test_attr")


@run_test_in_subprocess
def test_distributed():
    import distributed

    assert hasattr(distributed, "test_attr")
