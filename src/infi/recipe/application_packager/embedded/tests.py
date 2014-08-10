from unittest import SkipTest
from infi import unittest
from mock import patch
from glob import glob
from os import path, makedirs


EXPECTED_PYSTICK_ENVIRONMENT_FILE_CONTENTS = """env = DefaultEnvironment(
**{   'EXTERNAL_C_MODULES_FILE': './c_modules.json',
    'EXTERNAL_PY_MODULES_FILE': './python_files.json'}
)

"""

from . import build

class UnitTestCase(unittest.TestCase):
    def test_get_python_source(self):
        from . import python_source
        buildout_section = {'directory': '.'}
        buildout = dict({'isolated-python': {'version': 'v2.7.6'},
                                'buildout': buildout_section})
        options = dict(dict())
        with patch.object(python_source, "Download") as Download:
            with patch("tarfile.open") as tarfile_open:
                actual = python_source.get_python_source(buildout, options)
        source_url = "http://python.infinidat.com/python/sources/Python-2.7.6.tgz"
        args = Download(buildout_section)(source_url)[0], 'r:gz'
        tarfile_open.assert_called_with(*args)
        tarfile_open(*args).extract_all.assert_called()
        self.assertEquals(actual, path.join(path.curdir, 'build', 'Python-2.7.6'))

    def test_setup_wrapper(self):
        from ..utils import temporary_directory_context
        from . import setup
        from json import load
        with temporary_directory_context():
            expected_data = prepare_package_mock()
            setup.main()
            self.assertTrue(path.exists('_embed_recipe.json'))
            with open('_embed_recipe.json') as fd:
                data = load(fd)
        self.assertEquals(sorted(data['python_files']), sorted(expected_data['python_files']))
        self.assertEquals(sorted([sorted(extension.items()) for extension in data['c_extensions']]),
                          sorted([sorted(extension.items()) for extension in expected_data['c_extensions']]))

    def test_write_pystick_variable_file(self):
        from . import environment
        from ..utils import temporary_directory_context
        from os import name
        if name == 'nt':
            raise SkipTest("windows")
        with temporary_directory_context():
            environment.write_pystick_variable_file(path.join(path.curdir, 'pystick_variable_filepath'), [], [], {})
            with open('pystick_variable_filepath') as fd:
                actual = fd.read()
        self.assertEquals(actual, EXPECTED_PYSTICK_ENVIRONMENT_FILE_CONTENTS)

    def test_build_dependency(self):
        from . import build
        tgz = glob(path.join('.cache', 'dist', '*.tar.gz'))[0]
        egg = glob(path.join('.cache', 'dist', '*.egg'))[0]
        _zip = glob(path.join('.cache', 'dist', '*.zip'))[0]
        build.build_dependency(path.abspath(tgz))
        build.build_dependency(path.abspath(egg))
        build.build_dependency(path.abspath(_zip))


class MockedRecipeTestCase(unittest.TestCase):
    def test_executable(self):
        from infi.recipe.application_packager import embedded
        from ..utils import temporary_directory_context
        from . import environment
        buildout = dict(buildout={'directory': path.abspath(path.curdir),
                                  'download-cache': path.abspath(path.join(path.curdir, '.cache'))},
                        project=dict(name='infi.pyutils'))

        options = {}
        with temporary_directory_context():
            with patch.object(embedded.Executable, "prepare_sources"):
                with patch.object(embedded.Executable, "build_our_own_python_module") as build_our_own_python_module:
                    with patch.object(embedded, "run_in_another_process"):
                        build_our_own_python_module.return_value = [], []
                        recipe = embedded.Executable(buildout, 'name', options)
                        recipe.install()

    def test_static_library(self):
        from infi.recipe.application_packager import embedded
        from ..utils import temporary_directory_context
        from . import environment
        buildout = dict(buildout={'directory': path.abspath(path.curdir),
                                  'download-cache': path.abspath(path.join(path.curdir, '.cache'))},
                        project=dict(name='infi.pyutils'))

        options = {}
        with temporary_directory_context():
            with patch.object(embedded.StaticLibrary, "prepare_sources"):
                with patch.object(embedded.StaticLibrary, "build_our_own_python_module") as build_our_own_python_module:
                    with patch.object(embedded, "run_in_another_process"):
                        with patch.object(embedded.StaticLibrary, "copy_libfullpython"):
                            build_our_own_python_module.return_value = [], []
                            recipe = embedded.StaticLibrary(buildout, 'name', options)
                            recipe.install()


def prepare_package_mock():
    from pkg_resources import resource_string
    makedirs(path.join('src', 'hello', 'world'))
    with open(path.join('src', 'hello', '__init__.py'), 'w') as fd:
        fd.write("__import__('pkg_resources').declare_namespace(__name__)\n")
    with open(path.join('src', 'hello', 'world', '__init__.py'), 'w') as fd:
        fd.write("__import__('pkg_resources').declare_namespace(__name__)\n")
    with open(path.join('src', 'hello', 'world', 'foo.py'), 'w') as fd:
        pass
    with open('setup.py', 'w') as fd:
        fd.write(resource_string('infi.recipe.application_packager.embedded', 'setup.py.example'))
    python_files = [{u'name': u'hello',
                     u'package': True,
                     u'source': path.abspath(path.join(path.curdir, 'src', 'hello', '__init__.py'))},
                    {u'name': u'hello.world',
                     u'package': True,
                     u'source': path.abspath(path.join(path.curdir, 'src', 'hello', 'world', '__init__.py'))},
                    {u'name': u'hello.world.foo',
                     u'package': False,
                     u'source': path.abspath(path.join(path.curdir, 'src', 'hello', 'world', 'foo.py'))},
                    {u'name': u'bar',
                     u'package': False,
                     u'source': path.abspath(path.join(path.curdir, 'bar.py'))}]
    c_extensions = [{u'depends': [u'foo'],
                     u'env': {u'CCFLAGS': [],
                              u'CPPDEFINES': [u'THIS=1'],
                              u'CPPPATH': [path.abspath(path.join(path.curdir, 'include'))],
                              u'LINKFLAGS': []},
                     u'name': u'goodbye',
                     u'roots': [path.abspath('.')],
                     u'sources': [path.abspath(path.join(path.curdir, 'goodbye.c'))]}]
    return dict(python_files=python_files, c_extensions=c_extensions)
