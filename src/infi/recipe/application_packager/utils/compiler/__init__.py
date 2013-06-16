
from contextlib import contextmanager
from logging import getLogger
from glob import glob
from os import path
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

    def extract_package_name_from_source_filepath(self, filepath):
        [module_name] = [path.basename(filepath).replace(extension, '')
                         for extension in self.SOURCE_EXTENSIONS
                         if filepath.endswith(extension)]
        return module_name

    def get_installed_packages(self):
        from platform import python_version_tuple
        py_substring = 'py{}'.format('.'.join(python_version_tuple()[0:2]))
        all_installed_packages = [dirpath for dirpath in glob(path.join(self.eggs_directory, '*'))
                                  if path.isdir(dirpath) and not dirpath.endswith('{}.egg'.format(py_substring))]
        return all_installed_packages

    def extract_package_name_from_dirpath(self, dirpath):
        dirname = path.basename(dirpath)
        return dirname.split('-py')[0]

    def add_import_setuptools_to_setup_py(self):
        with open("setup.py") as fd:
            content = fd.read()
        content = content.replace("from distutils.core import setup", "from setuptools import setup")
        content = content.replace("from distutils import core", "import setuptools as core")
        with open("setup.py", 'w') as fd:
            fd.write(content)

    @contextmanager
    def extract_archive(self, archive_path):
        from archive import extract
        from .. import temporary_directory_context, chdir
        with temporary_directory_context() as tempdir:
            extract(archive_path, tempdir)
            [extracted_dir] = glob('*')
            with chdir(extracted_dir):
                yield extracted_dir

    def execute_with_isolated_python(self, commandline_or_args):
        import sys
        import os
        from infi.recipe.application_packager.utils.execute import execute_assert_success, parse_args
        from infi.recipe.application_packager.assertions import is_windows
        args = parse_args(commandline_or_args)
        executable = [os.path.join(self.buildout_directory, 'parts', 'python', 'bin',
                                   'python{}'.format('.exe' if is_windows() else ''))]
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.pathsep.join([path for path in sys.path])
        execute_assert_success(executable + args, env=env)

    def build_binary_egg(self):
        self.execute_with_isolated_python("setup.py bdist_egg".split())
        [egg] = glob(path.join('dist', '*.egg'))
        return egg

    def get_packages_to_install(self):
        source_archives = {self.extract_package_name_from_source_filepath(filename):
                           filename for filename in self.get_source_archives()}
        installed_binary_archives = {self.extract_package_name_from_dirpath(dirname): dirname
                                     for dirname in self.get_installed_packages()}
        # WORKAROUND python-cjson is installed as python_cjson
        keys_for_install_binary_archives = set(installed_binary_archives.keys())
        for key in list(keys_for_install_binary_archives):
            keys_for_install_binary_archives.add(key.replace('_', '-'))
        return [source_archives[key]
                for key in set.intersection(set(source_archives.keys()), keys_for_install_binary_archives)]

    def compile(self):
        from ..execute import ExecutionError
        from os import remove
        from shutil import copy
        for archive in self.get_packages_to_install():
            logger.info("Compiling egg for {}".format(archive))
            with self.extract_archive(archive) as extracted_dir:
                try:
                    built_egg = self.build_binary_egg()
                except ExecutionError:
                    self.add_import_setuptools_to_setup_py()
                    built_egg = self.build_binary_egg()
                copy(built_egg, self.archives_directory)
                remove(archive)

def compile_binary_distributions(buildout_directory, archives_directory, eggs_directory):
    BinaryDistributionsCompiler(buildout_directory, archives_directory, eggs_directory).compile()
