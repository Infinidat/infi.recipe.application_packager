import unittest
import mock
from infi.recipe.application_packager import utils
from os import path, curdir, name, pardir
from . import get_archive_path, long_one

is_windows = name == 'nt'

BUILDOUT_DIRECTORY = path.abspath(path.join(path.dirname(__file__), pardir))

import sys
if sys.version_info > (3, 0):
    patched_open_qualified_name = "builtins.open"
else:
    patched_open_qualified_name = "__builtin__.open"


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
