import unittest
from infi.pyutils.decorators import wraps
from os import environ, path, curdir, listdir

def get_archive_path(package_name):
    dist_dir = path.join(path.abspath(curdir), '.cache', 'dist')
    matches = [filename for filename in listdir(dist_dir) if filename.startswith(package_name)]
    if not matches:
        raise RuntimeError("Package not found in dist dir: {}".format(package_name))
    return path.join(dist_dir, matches[0])

def long_one(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if not environ.get("INCLUDE_LONG_TESTS"):
            raise unittest.SkipTest("To run this test, set environment variable INCLUDE_LONG_TESTS")
        return func(*args, **kwargs)
    return decorator
