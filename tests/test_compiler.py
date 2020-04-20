import unittest
import mock
from infi.recipe.application_packager import utils
from os import path, name, pardir, environ
from functools import wraps

is_windows = name == 'nt'

BUILDOUT_DIRECTORY = path.abspath(path.join(path.dirname(__file__), pardir))


def long_one(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if not environ.get("INCLUDE_LONG_TESTS"):
            raise unittest.SkipTest("To run this test, set environment variable INCLUDE_LONG_TESTS")
        return func(*args, **kwargs)
    return decorator


class CompilerTestCase(unittest.TestCase):
    def setUp(self):
        if is_windows:
            raise unittest.SkipTest("Not applicable on Windows")

    def get_compiler(self):
        compiler = utils.compiler.BinaryDistributionsCompiler(buildout_directory=BUILDOUT_DIRECTORY,
                                                              archives_directory=path.join(".cache", "dist"),
                                                              eggs_directory='eggs')
        return compiler

    @long_one
    def test_compile_all(self):
        with mock.patch("os.remove"), mock.patch("shutil.copy"):
            utils.compiler.compile_binary_distributions(buildout_directory=BUILDOUT_DIRECTORY,
                                                        archives_directory=path.join(".cache", "dist"),
                                                        eggs_directory='eggs')
