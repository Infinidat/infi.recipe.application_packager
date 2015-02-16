import unittest
import mock
from infi.recipe.application_packager import utils
from os import path, curdir, name, pardir
from . import get_archive_path, long_one

is_windows = name == 'nt'

BUILDOUT_DIRECTORY = path.abspath(path.join(path.dirname(__file__), pardir))

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
        lxml_archive = get_archive_path("async-0.6.2.tar.gz")
        compiler = self.get_compiler()
        with compiler.extract_archive(lxml_archive):
            compiler.add_import_setuptools_to_setup_py()
            built_egg = compiler.build_binary_egg()
            self.assertTrue(path.exists(built_egg))

    def test_get_packages_to_install(self):
        expected = [get_archive_path("coverage-3.7.1.tar.gz"),
                    get_archive_path("gitdb-0.6.4.tar.gz"),
                    get_archive_path("PyYAML-3.11.zip"),
                    get_archive_path("pycrypto-2.6.1.tar.gz"),
                    get_archive_path("MarkupSafe-0.23.tar.gz"),
                    get_archive_path("psutil-2.2.1.tar.gz")]
        actual = self.get_compiler().get_packages_to_install()
        self.assertEquals(set(actual), set(expected))

    @long_one
    def test_compile_all(self):
        with mock.patch("os.remove"), mock.patch("shutil.copy"):
            utils.compiler.compile_binary_distributions(buildout_directory=BUILDOUT_DIRECTORY,
                                                        archives_directory=path.join(".cache", "dist"),
                                                        eggs_directory='eggs')

    def test_setup_requires(self):
        with mock.patch.object(utils.compiler.BinaryDistributionsCompiler, 'extract_archive'):
            with open(path.join('tests', 'file_with_setup_requires')) as fd:
                xreadlines = iter(fd.readlines())
                with mock.patch('__builtin__.open') as _open:
                    _open('setup.py').__enter__.return_value.xreadlines = lambda: xreadlines
                    instance = utils.compiler.BinaryDistributionsCompiler(buildout_directory=BUILDOUT_DIRECTORY,
                                                                          archives_directory=path.join(".cache", "dist"),
                                                                          eggs_directory='eggs'
                                                                          )
                    self.assertTrue(instance.does_setup_py_uses_setup_requires('x'))
