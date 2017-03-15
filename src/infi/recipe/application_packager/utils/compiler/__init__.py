from contextlib import contextmanager
from logging import getLogger
from glob import glob
from os import path, linesep
from itertools import chain

logger = getLogger(__name__)

class BinaryDistributionsCompiler(object):
    SOURCE_EXTENSIONS =  ['.zip', '.tar.gz', '.tar.bz2']
    def __init__(self, buildout_directory, archives_directory, eggs_directory):
        from os.path import abspath
        super(BinaryDistributionsCompiler, self).__init__()
        self.buildout_directory = buildout_directory
        self.archives_directory = abspath(archives_directory)
        self.eggs_directory = abspath(eggs_directory)

    def get_source_archives(self):
        all_sources = [glob(path.join(self.archives_directory, '*{}'.format(extension)))
                       for extension in self.SOURCE_EXTENSIONS]
        all_sources = list(chain.from_iterable(all_sources))
        return all_sources

    def add_import_setuptools_to_setup_py(self):
        with open("setup.py") as fd:
            content = fd.read()
        if 'distutils' in content:
            content = content.replace("distutils.core", "setuptools")
            content = content.replace("from distutils import core", "import setuptools as core")
        else:
            content = 'import setuptools' + linesep + content
        with open("setup.py", 'w') as fd:
            fd.write(content)

    @contextmanager
    def extract_archive(self, archive_path):
        import tarfile
        from zipfile import ZipFile
        from .. import temporary_directory_context, chdir
        archive_opener = tarfile.open if archive_path.endswith('gz') else ZipFile
        with temporary_directory_context() as tempdir:
            with archive_opener(archive_path) as open_archive:
                open_archive.extractall(tempdir)
            archive_files = glob('*')
            if len(archive_files) == 1: # all files are under a sub-directory
                with chdir(archive_files[0]):
                    yield archive_files[0]
            else:
                yield tempdir

    def build_egg(self, setup_script="setup.py"):
        execute_with_isolated_python(self.buildout_directory, [setup_script, "bdist_egg"])
        [egg] = glob(path.join('dist', '*.egg'))
        return egg

    def compile_eggs(self):
         from ..execute import ExecutionError
         from os import remove
         from shutil import copy
         for archive in self.get_source_archives():
             logger.info("Compiling egg for {}".format(archive))
             with self.extract_archive(archive) as extracted_dir:
                 try:
                     built_egg = self.build_egg("setupegg.py" if path.exists("setupegg.py") else "setup.py")
                 except ExecutionError:
                     self.add_import_setuptools_to_setup_py()
                     built_egg = self.build_egg()
                 copy(built_egg, self.archives_directory)
                 remove(archive)

    def compile_wheels(self):
        from ..execute import ExecutionError
        from .. import chdir
        from os import remove
        from shutil import copy
        with chdir(self.archives_directory):
            for archive in self.get_source_archives():
                logger.info("Compiling wheel for {}".format(archive))
                execute_with_isolated_python(self.buildout_directory, ["-m", "pip", "wheel", "--no-deps", archive])
                remove(archive)

    def compile(self):
        return self.compile_wheels()


def execute_with_isolated_python(buildout_directory, commandline_or_args, **kwargs):
    import sys
    import os
    from infi.recipe.application_packager.utils.execute import execute_assert_success, parse_args
    from infi.recipe.application_packager.assertions import is_windows
    args = parse_args(commandline_or_args)
    executable = [os.path.join(buildout_directory, 'parts', 'python', 'bin',
                               'python{}'.format('.exe' if is_windows() else ''))]
    env = kwargs.pop('env', os.environ.copy())
    env['PYTHONPATH'] = ''
    execute_assert_success(executable + args, env=env, **kwargs)


def compile_binary_distributions(buildout_directory, archives_directory, eggs_directory, build_wheels):
    compiler = BinaryDistributionsCompiler(buildout_directory, archives_directory, eggs_directory)
    if build_wheels:
        compiler.compile_wheels()
    else:
        compiler.compile_eggs()


def byte_compile_lib(buildout_directory):
    libdir = path.join("parts", "python", "lib64")
    if not path.exists(libdir):
        libdir = path.join("parts", "python", "lib")
    execute_with_isolated_python(buildout_directory,
                                 ["-m", "compileall", libdir],
                                 allowed_return_codes=[0, 1])
