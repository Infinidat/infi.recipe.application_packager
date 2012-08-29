import unittest
from infi.pyutils.decorators import wraps
from os import environ, path

def get_archive_path(filename):
    return path.join(path.abspath(curdir), '.cache', 'dist', filename)

def long_one(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if not environ.get("INCLUDE_LONG_TESTS"):
            raise unittest.SkipTest("To run this test, set environment variable INCLUDE_LONG_TESTS")
        return func(*args, **kwargs)
    return decorator
