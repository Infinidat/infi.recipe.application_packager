from infi import unittest
from mock import patch
from glob import glob
from os import path, makedirs


EXPECTED_PYSTICK_ENVIRONMENT_FILE_CONTENTS = """STATIC_PYTHON_MODULES=1
PRECOMPILED_STATIC_LIBS=[]
XFLAGS='xflags'
EXTERNAL_PY_MODULES_FILE='./python_files.json'
EXTERNAL_C_MODULES_FILE='./c_modules.json'
HAVE_CURSES=1
HAVE_CURSES_PANEL=1
HAVE_LIBBZ2=1
HAVE_LIBCABINET=1
HAVE_LIBCRYPT=1
HAVE_LIBDB=1
HAVE_LIBGDBM=1
HAVE_LIBM=1
HAVE_LIBNSL=1
HAVE_LIBRPCRT4=1
HAVE_LIBSQLITE3=1
HAVE_LIBTCL=0
HAVE_LIBTK=0
HAVE_LIBWS32_32=1
HAVE_LIBZ=1
HAVE_OPENSSL=1
HAVE_READLINE=1
WITH_PYTHON_MODULE_NIS=0
"""


from . import build

class UnitTestCase(unittest.TestCase):
    def test_get_python_source(self):
        from . import source
        buildout_section = {'directory': '.'}
        buildout = dict({'isolated-python': {'version': 'v2.7.6'},
                                'buildout': buildout_section})
        options = dict(dict())
        with patch.object(source, "Download") as Download:
            with patch("tarfile.open") as tarfile_open:
                actual = source.get_python_source(buildout, options)
        source_url = "http://python.infinidat.com/archives/Python-2.7.6.tgz"
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
        self.assertEquals(sorted(data['c_extensions']), sorted(expected_data['c_extensions']))

    def test_get_static_libraries(self):
        from . import environment
        with patch.object(environment, 'glob') as glob:
            glob.return_value = [path.join('a', 'libfoo.a'), path.join('a', 'libpython2.7.a')]
            actual = environment.get_static_libraries('a')
        self.assertEquals(actual, [path.join('a', 'libfoo.a')])
        glob.assert_called_with(path.join('a', '*'))

    def test_get_names_from_static_libdir(self):
        from . import environment
        with patch.object(environment, 'glob') as glob:
            glob.return_value = [path.join('a', 'libfoo.a'), path.join('a', 'libpython2.7.a')]
            actual = environment.get_names_from_static_libdir('a')
        self.assertEquals(actual, [path.join('foo')])
        glob.assert_called_with(path.join('a', '*'))

    def test_get_xflags(self):
        from . import environment
        with patch.object(environment, 'get_names_from_static_libdir') as get_names_from_static_libdir:
            get_names_from_static_libdir.return_value = ['ncurses', 'foo', 'bar']
            with patch.object(environment, 'system') as system:
                system.return_value = 'NonExistingOS'
                actual = environment.get_xflags('a', dict(xflags='foo'))
        self.assertNotEquals(actual, '')

    def test_write_pystick_variable_file(self):
        from . import environment
        from ..utils import temporary_directory_context
        with temporary_directory_context():
            environment.write_pystick_variable_file(path.join(path.curdir, 'pystick_variable_filepath'), [], [], 'xflags', [])
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
                    with patch.object(environment, "get_xflags") as get_xflags:
                        with patch.object(embedded, "run_in_another_process"):
                            get_xflags.return_value = ''
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
                    with patch.object(environment, "get_xflags") as get_xflags:
                        with patch.object(embedded, "run_in_another_process"):
                            with patch.object(embedded.StaticLibrary, "copy_libfullpython"):
                                get_xflags.return_value = ''
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
                     u'env': {u'CPPDEFINES': [u'THIS=1'],
                              u'CPPPATH': [path.abspath(path.join(path.curdir, 'include'))],
                              u'LINKFLAGS': []},
                     u'name': u'goodbye',
                     u'roots': [path.abspath('.')],
                     u'sources': [path.abspath(path.join(path.curdir, 'goodbye.c'))]}]
    return dict(python_files=python_files, c_extensions=c_extensions)