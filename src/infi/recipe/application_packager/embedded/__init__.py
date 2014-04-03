__import__("pkg_resources").declare_namespace(__name__)

from logging import getLogger
from ..base import PackagingRecipe, RECIPE_DEFAULTS
from .. import utils
from glob import glob
from os import path, curdir, makedirs, listdir, remove, chdir, symlink
from shutil import rmtree, copy
from pkg_resources import resource_filename
from infi.pyutils.contexts import contextmanager
from infi.pyutils.lazy import cached_method
from infi.execute import execute_assert_success

logger = getLogger(__name__)

DEFINES = ["HAVE_CURSES=1", "HAVE_CURSES_PANEL=1", "HAVE_LIBBZ2=1", "HAVE_LIBCABINET=1", "HAVE_LIBCRYPT=1",
           "HAVE_LIBDB=1", "HAVE_LIBGDBM=1", "HAVE_LIBM=1", "HAVE_LIBNSL=1",
           "HAVE_LIBRPCRT4=1", "HAVE_LIBSQLITE3=1", "HAVE_LIBTCL=0", "HAVE_LIBTK=0", "HAVE_LIBWS32_32=1",
           "HAVE_LIBZ=1", "HAVE_OPENSSL=1", "HAVE_READLINE=1",
           "WITH_PYTHON_MODULE_NIS=0"]
PYTHON_SOURCE = "ftp://python.infinidat.com/archives/Python-2.7.6.tgz"
PYTHON_SCRIPT = path.abspath(path.join(path.curdir, 'bin', 'python'))
PYTHON_EXECUTABLE = path.abspath(path.join(path.curdir, 'parts', 'python', 'bin', 'python'))

SETUP_PY_MOCK = """import setuptools
import subprocess
import distutils.core
import json
import mock
import os

_setup_called = False

def _scan(package, dirpath):
    python_files = []
    prefix = package if os.path.exists(os.path.join(dirpath, '__init__.py')) else ''
    pid = subprocess.Popen(["find", dirpath, "-name", "*.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = pid.communicate()
    for py in stdoutdata.splitlines():
        name = prefix + '.' + os.path.relpath(py, os.path.abspath(dirpath)).replace(".py", '').replace("__init__", '')
        name = name.replace(os.path.sep, '.').strip('.')
        if ' ' in name:
            continue
        python_files.append(dict(package="__init__.py" in py, source=os.path.abspath(py), name=name))
    return python_files

def _setup(name, package_dir={}, packages={}, ext_modules=[], py_modules=[], **kwargs):
    global _setup_called
    _setup_called = True
    python_files, c_extensions = [], []
    previous_package = '*'
    for package in packages:
        if previous_package in package:
            break
        dirpath = os.path.abspath(package_dir.get('', package))
        python_files.extend(_scan(package, dirpath))
        previous_package = package
    for ext_module in ext_modules:
        env = dict(CPPDEFINES=["{}={}".format(item[0], item[1]) for item in ext_module.define_macros])
        c_extensions.append(dict(name=ext_module.name,
                                 sources=[os.path.abspath(source) for source in ext_module.sources],
                                 roots=list(set([os.path.abspath(os.path.dirname(source)) for source in ext_module.sources])),
                                 depends=ext_module.depends, env=env))
    for py_module in py_modules:
        python_files.append(dict(package=False, source=os.path.abspath(py_module + '.py'), name=py_module))
    with open("_embed_recipe.json", 'w') as fd:
        fd.write(json.dumps(dict(python_files=python_files, c_extensions=c_extensions)))

with mock.patch.object(setuptools, "setup", new=_setup):
    with mock.patch.object(distutils.core, "setup", new=_setup):
        with open('setup.py') as fd:
            exec(fd.read())
"""

@contextmanager
def chdir_context(dirpath):
    global last_directory
    before = path.abspath(path.curdir)
    try:
        yield chdir(dirpath)
    finally:
        last_directory = dirpath
        chdir(before)

class Recipe(PackagingRecipe):
    def install(self):
        """:returns: a list of installed filepaths"""
        self.download_and_install_python_source()
        utils.download_buildout(self.get_download_cache_dist())
        utils.download_distribute(self.get_download_cache_dist())
        utils.download_setuptools(self.get_download_cache_dist())
        self.build_embedded_python()
        return self.get_embedded_python_files()

    def get_embedded_python_files(self):
        return [] # TODO

    @property
    @cached_method
    def buildout_directory(self):
        return self.get_buildout_section().get('directory')

    def download_and_install_python_source(self):
        # inspired from infi.recipe.python

        def download():
            from zc.buildout.download import Download
            source_url = self.get_recipe_section().get('python-source-url', PYTHON_SOURCE)
            logger.info("downloading {}".format(source_url))
            downloader = Download(self.get_buildout_section())
            return downloader(source_url)[0]

        def install(filepath):
            import tarfile
            extract_path = path.join(self.buildout_directory, 'parts')
            archive = tarfile.open(filepath, 'r:gz')
            logger.info("extracting {}".format(filepath))
            archive.extractall(extract_path)
            extracted_files = archive.getnames()
            archive.close()
            return extracted_files

        return install(download())

    def get_isolated_python_directories(self, prefix):
        directories = []
        buildout_directory = self.get_buildout_section().get('directory')
        for prefix_dirpath in glob(path.join(buildout_directory, 'parts', 'python', prefix + '*')):
            directories.append(prefix_dirpath)
            directories.extend([dirpath for dirpath in glob(path.join(prefix_dirpath, "*"))
                                if 'python2.7' not in dirpath and path.isdir(dirpath)])
        return directories

    def get_include_dirs(self):
        return self.get_isolated_python_directories("include")

    def get_library_dirs(self):
        return self.get_isolated_python_directories("lib")

    def print_log_files(self):
        embedded_dirpath = path.join(self.get_buildout_section().get('directory'), 'parts', 'python.embedded')
        log_files = [path.join(embedded_dirpath, 'configure.log'), path.join(embedded_dirpath, 'vars')]
        for filepath in log_files:
            print '-'*79
            print filepath
            print '+'*79
            with open(filepath) as fd:
                print fd.read()

    def run_pystick(self, args):
        from pystick import pack
        logger.info(' '.join(repr(item) for item in args))
        try:
            with chdir_context('.'):
                pack.main(args)
        except SystemExit, error:
            if error.code == 0:
                return
            if self.get_recipe_section().get('debug', 'false') == 'true':
                self.print_log_files()
            raise

    def build_embedded_python(self):
        from os import environ
        source_url = self.get_recipe_section().get('python-source-url', PYTHON_SOURCE)
        source_path = path.join(self.buildout_directory, 'parts', source_url.rsplit('/', 1)[-1].rsplit('.', 1)[0])
        build_path = path.join(self.buildout_directory, 'parts', 'python.embedded')
        if not path.exists(build_path):
            makedirs(build_path)
        variable_file = self.write_variable_file()
        args = ["PYTHON_SOURCE_PATH={}".format(source_path), "BUILD_PATH={}".format(build_path),
                "--vars={}".format(variable_file)]
        self.run_pystick(args)

    def copy_static_libraries_from_isolated_python(self):
        from tempfile import mkdtemp
        static_libdir = mkdtemp()
        buildout_directory = self.buildout.get('buildout').get('directory')
        for filepath in glob(path.join(buildout_directory, 'parts', 'python', 'lib*', '*.a')):
            copy(filepath, static_libdir)
        return static_libdir, [path.basename(item.rsplit('.', 1)[0])[3:] for item in glob(path.join(static_libdir, '*'))]

    def get_xflags(self):
        from sysconfig import get_config_var
        from platform import system
        static_dir, static_libs = self.copy_static_libraries_from_isolated_python()
        static_libs.remove('ncurses')
        static_libs.append('ncurses')
        static_libs_formatted = ' '.join(['-l{}'.format(item) for item in static_libs
                                          for item in static_libs if not item.endswith('_g')])
        xflags = ' '.join([get_config_var('CFLAGS'),
                           '-L{}'.format(static_dir), get_config_var('LDFLAGS'),
                           get_config_var("SHLIBS"), get_config_var("SYSLIBS"),
                           static_libs_formatted])
        if system() == 'Darwin':
            xflags += ' -framework SystemConfiguration'
        elif system() == 'Linux':
            xflags += ' -lcrypt'
        return xflags

    def write_variable_file(self):
        from platform import system
        from sysconfig import get_config_vars
        variable_filepath = path.join(self.buildout_directory, 'parts', 'python.embedded', 'vars')
        external_modules_dict = self.get_external_modules_files()
        with open(variable_filepath, 'w') as fd:
            for key, value in get_config_vars().items():
                fd.write("{}={!r}\n".format(key, value))
            fd.write("XFLAGS={!r}\n".format(self.get_xflags()))
            for key, value in external_modules_dict.items():
                fd.write("{}={!r}\n".format(key, value))
                fd.write("STATIC_PYTHON_MODULES=1\n")
            for item in DEFINES:
                fd.write("{}\n".format(item))
        return variable_filepath


    def _scan_for_files_with_setup_py(self, build_dir):
        from os import name
        from json import loads
        python_files, c_extensions = [], []
        with chdir_context(build_dir):
            setup_py_mock = "_embed_recipe.py"
            setup_py_mock_json = "_embed_recipe.json"
            with open(setup_py_mock, 'w') as fd:
                fd.write(SETUP_PY_MOCK)
            cmd = [PYTHON_EXECUTABLE, PYTHON_SCRIPT, setup_py_mock] if name != 'nt' else \
                  [PYTHON_SCRIPT, setup_py_mock]
            logger.info(' '.join(cmd))
            execute_assert_success(cmd)
            with open(setup_py_mock_json) as fd:
                return loads(fd.read())

    def _scan_egg_dir(self, build_dir):
        python_files, c_extensions = [], []
        for dirpath in glob(path.join(build_dir, '*')):
            if not path.isdir(dirpath):
                continue
            if not path.basename(dirpath) in build_dir:
                continue
            for py in execute_assert_success(["find", dirpath, "-name", "*.py"]).get_stdout().splitlines():
                name = py.replace(build_dir, '').replace(".py", '').replace("__init__", '')
                name = name.strip(path.sep).replace(path.sep, '.')
                if ' ' in name:
                    continue
                python_files.append(dict(package="__init__.py" in py, source=path.abspath(py), name=name))
        return dict(python_files=python_files, c_extensions=c_extensions)

    def build_dependency(self, filepath):
        """:returns: base directory"""
        from os import name

        def _unzip_egg(basename):
            dirname = basename.rsplit('-', 1)[0]
            if not path.exists(dirname):
                makedirs(dirname)
            with chdir_context(dirname):
                execute_assert_success(['unzip', '-f', path.join(path.pardir, basename)])
            return dirname

        def _extract_and_build_tgz(basename):
            dirname = basename.rsplit('.', 2)[0]
            execute_assert_success(['tar', 'zxf', basename])
            with chdir_context(dirname):
                cmd = [PYTHON_EXECUTABLE, PYTHON_SCRIPT, 'setup.py', 'build'] if name != 'nt' else \
                      [PYTHON_SCRIPT, 'setup.py', 'build']
                logger.info(' '.join(cmd))
                execute_assert_success(cmd)
            return dirname

        with chdir_context(path.join('.cache', 'dist')):
            basename = path.basename(filepath)
            logger.info("building {}".format(basename))
            if basename.endswith('egg'):
                return path.join('.cache', 'dist', _unzip_egg(basename))
            elif basename.endswith('zip'):
                execute_assert_success(['unzip', '-f', basename])
                return path.join('.cache', 'dist', basename.rsplit('.', 1)[0])
            elif basename.endswith('gz'):
                return path.join('.cache', 'dist', _extract_and_build_tgz(basename))
            else:
                raise RuntimeError()

    def scan_for_files(self, build_dir):
        """:returns: dict of python_files, c_extenstions"""
        logger.info("scanning {}".format(build_dir))
        if path.exists(path.join(build_dir, 'setup.py')):
            return self._scan_for_files_with_setup_py(build_dir)
        return self._scan_egg_dir(build_dir)

    def get_dependencies_for_embedding(self):
        from ..utils import get_dependencies, get_distributions_from_dependencies
        eggs = self.get_eggs_for_production().split() or [self.get_python_module_name()]
        dependencies = set.union(set(eggs), *[get_dependencies(name) for name in eggs])
        distributions = get_distributions_from_dependencies(dependencies)
        return distributions

    def iter_archives_for_embedding(self):
        distributions = self.get_dependencies_for_embedding()
        for filepath in glob(path.join(self.get_download_cache_dist(), '*')):
            if path.isdir(filepath):
                continue
            if 'zc.' in filepath:
                continue
            basename = path.basename(filepath).lower()
            if any([distname.lower() in basename and version.replace('-', '_') in basename.replace('-', '_')
                   for distname, version in distributions.items()]):
                yield filepath

    def get_external_modules(self):
        python_files = []
        c_extensions = []
        for filepath in self.iter_archives_for_embedding():
            build_dir = self.build_dependency(filepath)
            files = self.scan_for_files(build_dir)
            python_files.extend(files['python_files'])
            c_extensions.extend(files['c_extensions'])
        my_files = self.scan_for_files(path.curdir)
        python_files.extend(my_files['python_files'])
        c_extensions.extend(my_files['c_extensions'])
        return python_files, c_extensions

    def get_external_modules_files(self):
        """:returns: dict"""
        from json import dumps
        python_files, c_extensions = self.get_external_modules()
        python_modules_file = path.join(self.buildout_directory, 'parts', 'python.embedded', 'python_files.json')
        c_modules_file = path.join(self.buildout_directory, 'parts', 'python.embedded', 'c_modules.json')
        with open(python_modules_file, 'w') as fd:
            fd.write(dumps(python_files))
        with open(c_modules_file, 'w') as fd:
            fd.write(dumps(c_extensions, indent=4))
        return dict(EXTERNAL_PY_MODULES_FILE=python_modules_file, EXTERNAL_C_MODULES_FILE=c_modules_file)

    def update(self):
        pass


class Executable(Recipe):
    def get_compile_flags(self):
        raise NotImplementedError()


class SharedLibrary(Recipe):
    def get_compile_flags(self):
        raise NotImplementedError()

