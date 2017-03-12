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

    def test_compile_async(self):
        try:
            archive_to_compile = get_archive_path("psutil")
            compiler = self.get_compiler()
            with compiler.extract_archive(archive_to_compile):
                compiler.add_import_setuptools_to_setup_py()
                built_egg = compiler.build_binary_egg()
                self.assertTrue(path.exists(built_egg))
        except RuntimeError:
            raise unittest.SkipTest("This test must be run before test_installer")

    def test_get_packages_to_install(self):
        try:
            actual = self.get_compiler().get_packages_to_install()
            expected = [get_archive_path("mock"),
                        get_archive_path("infi.recipe.python"),
                        get_archive_path("buildout.wheel"),
                        get_archive_path("pbr"),
                        get_archive_path("funcsigs"),
                        get_archive_path("scandir"),
                        get_archive_path("MarkupSafe"),
                        get_archive_path("psutil"),
                        get_archive_path("Logbook"),
                        ]
            self.assertEquals(set(actual), set(expected))
        except RuntimeError:
            raise unittest.SkipTest("This test must be run before test_installer")

    @long_one
    def test_compile_all(self):
        with mock.patch("os.remove"), mock.patch("shutil.copy"):
            utils.compiler.compile_binary_distributions(buildout_directory=BUILDOUT_DIRECTORY,
                                                        archives_directory=path.join(".cache", "dist"),
                                                        eggs_directory='eggs')

    def test_setup_requires(self):
        with mock.patch.object(utils.compiler.BinaryDistributionsCompiler, 'extract_archive'):
            with open(path.join('tests', 'file_with_setup_requires')) as fd:
                with mock.patch(patched_open_qualified_name) as _open:
                    _open('setup.py').__enter__.return_value.__iter__.return_value = iter(fd)
                    instance = utils.compiler.BinaryDistributionsCompiler(buildout_directory=BUILDOUT_DIRECTORY,
                                                                          archives_directory=path.join(".cache", "dist"),
                                                                          eggs_directory='eggs'
                                                                          )
                    self.assertTrue(instance.does_setup_py_uses_setup_requires('x'))
