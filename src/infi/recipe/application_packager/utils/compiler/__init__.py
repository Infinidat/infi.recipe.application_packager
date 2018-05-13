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


def compile_binary_distributions(buildout_directory, archives_directory, eggs_directory):
    compiler = BinaryDistributionsCompiler(buildout_directory, archives_directory, eggs_directory)
    compiler.compile_wheels()


def byte_compile_lib(buildout_directory):
    libdir = path.join("parts", "python", "lib64")
    if not path.exists(libdir):
        libdir = path.join("parts", "python", "lib")
    execute_with_isolated_python(buildout_directory,
                                 ["-m", "compileall", libdir],
                                 allowed_return_codes=[0, 1])
