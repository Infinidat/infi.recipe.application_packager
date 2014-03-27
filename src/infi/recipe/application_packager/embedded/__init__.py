__import__("pkg_resources").declare_namespace(__name__)

from logging import getLogger
from ..base import PackagingRecipe, RECIPE_DEFAULTS
from .. import utils
from glob import glob
from os import path, curdir, makedirs, listdir, remove
from shutil import rmtree, copy
from pkg_resources import resource_filename

logger = getLogger(__name__)

PYTHON_SOURCE = "ftp://python.infinidat.com/archives/Python-2.7.6.tgz"
LIBRARIES = "-lm -lz -lbz2 -ldb -lncurses -lpanel -lreadline -lcrypt -lnsl -lssl -lcrypto -lutil -ldl"

class Recipe(PackagingRecipe):
    def install(self):
        """:returns: a list of installed filepaths"""
        self.download_and_install_python_source()
        self.build_pare_python()
        self.generate_file_list()
        # CFLAGS, LIBS, …
        # List of pure-python files
        # List of C extensions
        # Bindings instructions
        return []

    def download_python_source(self):
        # inspired from infi.recipe.python
        from zc.buildout.download import Download
        import tarfile
        buildout_directory = self.buildout.get('buildout').get('directory')
        extract_path = path.join(buildout_directory, 'parts')
        source_url = self.options.get('python-source-url', PYTHON_SOURCE)
        downloader = Download(self.buildout.get('buildout'))
        source_filepath = downloader(source_url)[0]
        archive = tarfile.open(source_filepath, 'r:gz')
        archive.extractall(extact_path)
        extracted_files = archive.getnames()
        archive.close()
        for filepath in [sep.join([self.extact_path, filename]) for filename in files]:
            self.options.created(filepath)

    def get_include_dirs(self):
        include_dir = path.join(buildout_directory, 'parts', 'python', 'include')
        return [include_dir] + [dirpath for dirpath in glob(path.join(include_dir, "*"))
                                if 'python2.7' not in dirpath and path.isdir(dirpath)]

    def get_library_dirs(self):
        lib_dir = path.join(buildout_directory, 'parts', 'python', 'lib')
        return [lib_dir] + [dirpath for dirpath in glob(path.join(lib_dir, "*"))
                            if 'python2.7' not in dirpath and path.isdir(dirpath)]

    def build_bare_python(self):
        from infi.execute import execute_assert_success
        source_url = self.options.get('python-source-url', PYTHON_SOURCE)
        source_path = path.join(buildout_directory, 'parts', source_url.rsplit('/', 1)[-1].rsplit('.', 1)[0])
        build_path = path.join(buildout_directory, 'parts', 'bare_python')
        include_path = " ".join(["-I{}".format(item) for item in sel.get_include_dirs()])
        library_path = " ".join(["-L{}".format(item) for item in sel.get_library_dirs()])
        args = ["PYTHON_SOURCE_PATH={}".format(source_path), "BUILD_PATH={}".format(build_path),
                "XFLAGS={-pthread -g {0} {1} {2}".format(include_path, library_path, LIBRARIES),
                "HAVE_CURSES=1", "HAVE_READLINE=1", "HAVE_LIBM=1", "HAVE_LIBZ=1", "HAVE_LIBCRYPT=1", "HAVE_OPENSSL=1",
                "HAVE_LIBCRYPTO=1", "HAVE_LIBDL=1", "HAVE_LIBNSL=1"]
        execute_assert_success(["bin/pack"] + args)

    def get_dependencies_for_embedding(self):
        from ..utils import get_dependencies, get_distributions_from_dependencies
        eggs = self.get_eggs_for_production().split() or [self.get_python_module_name()]
        dependencies = set.union(set(eggs), *[get_dependencies(name) for name in eggs])
        distributions = get_distributions_from_dependencies(dependencies)
        return distributions

    def iter_archives_for_embedding(self):
        distributions = self.get_dependencies_for_embedding()
        for filepath in glob(path.join(self.get_download_cache_dist(), '*')):
            basename = path.basename(filepath).lower()
            if any([distname.lower() in basename and version.replace('-', '_') in basename.replace('-', '_')
                   for distname, version in distributions.items()]):
                yield filepath

    def build_dependency(self, filepath):
        # if .egg then just extract it
        # else
        # fix setuptools import
        # run setup.py install with a monkey-patches version of setuptools?
        # this is to hack around the C extensions
        raise NotImplementedError()

    def generate_file_list(self):
        for filepath in self.iter_archives_for_embedding():
            self.build_depedency(filepath)

    def update(self):
        pass


class Executable(Recipe):
    def get_compile_flags(self):
        raise NotImplementedError()


class SharedLibrary(Recipe):
    def get_compile_flags(self):
        raise NotImplementedError()

