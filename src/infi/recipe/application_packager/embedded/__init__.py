__import__("pkg_resources").declare_namespace(__name__)

from infi.recipe.application_packager.utils import chdir as chdir_context
from infi.recipe.application_packager.base import PackagingRecipe
from pkg_resources import resource_string, ensure_directory
from infi.execute import execute_assert_success
from infi.pyutils.lazy import cached_method
from logging import getLogger
from platform import system
from shutil import copy
from glob import glob
from os import path

logger = getLogger(__name__)
MAIN = resource_string(__name__, 'main.c')
SCONSTRUCT = resource_string(__name__, 'SConstruct')

def pystick(args):
    import sys
    from pystick import pack
    sys.argv = ['scons']
    logger.info(' '.join(repr(item) for item in args))
    pack.main(args)


def scons(args=None):
    import sys
    from SCons import Script
    sys.argv = ['csons'] + (args or list())
    Script.main()


def run_in_another_process(target, args):
    # scons uses a lot of global variables, makes it impossible to run two difference
    # scons files under the same processes
    from multiprocessing import Process
    process = Process(target=target, args=(args,))
    process.start()
    process.join()
    if process.exitcode > 0:
        raise RuntimeError(process.exitcode)


class Recipe(PackagingRecipe):
    def prepare_sources(self):
        """
        downloads Python source, setuptools and zc.build prepare_sources to .cache/dist
        :returns: path of extracted Python source
        """
        from . import source
        from .. import utils
        assert path.exists(self.isolated_python_dirpath)
        utils.download_buildout(self.get_download_cache_dist())
        utils.download_distribute(self.get_download_cache_dist())
        utils.download_setuptools(self.get_download_cache_dist())
        return source.get_python_source(self.buildout, self.options)

    def build_embedded_python(self, python_source_path):
        if glob(path.join(self.embedded_python_build_dir, '*fpython*')):
            logger.debug("embedded python is already built, skipping it")
            return
        self.prepare_for_running_pystick()
        args = ["PYTHON_SOURCE_PATH={}".format(python_source_path),
                "BUILD_PATH={}".format(self.embedded_python_build_dir),
                "--defaultenv={}".format(self.pystick_variable_filepath)]
        run_in_another_process(pystick, args)

    def prepare_for_running_pystick(self):
        if path.exists(self.pystick_variable_filepath):
            logger.info("pystick file {!r} exists, skipping re-writing it")
            return
        # before running pystick, we need to do some stuff
        self.copy_static_libraries_from_isolated_python()
        # dependnecies may have C extensions, we need to pass their sources to pystick
        # because the sources are not written to the eggs directory,
        # we need to extract the sources and "build" them on our to learn of the sources
        python_files, c_extensions = self.build_dependencies()
        # build our own sources (again, for handling C extension)
        our_python_files, our_c_extensions = self.build_our_own_python_module()
        python_files.extend(our_python_files)
        c_extensions.extend(our_c_extensions)
        # and at last
        self.write_pystick_variable_file(python_files, c_extensions)

    def copy_static_libraries_from_isolated_python(self):
        extension = dict(Darwin='a', Linux='a', Windows="lib")[system()]
        for src in glob(path.join(self.isolated_python_dirpath, 'lib*', '*.{}'.format(extension))):
            if src.rsplit('.', 1)[0].endswith("_g") or 'python2.7' in src:
                continue
            if path.basename(src).startswith('_'):
                continue
            if system() == 'Windows' and 'pyexpat' in src:
                continue
            dst = path.join(self.static_libdir, path.basename(src))
            ensure_directory(dst)
            copy(src, dst) if not path.exists(dst) else None

    def build_dependencies(self):
        from .build import build_setup_py, build_dependency, scan_for_files
        python_files, c_extensions = [], []
        for filepath in self.iter_archives_for_embedding():
            build_dir = build_dependency(filepath)
            files = scan_for_files(build_dir)
            python_files.extend(files['python_files'])
            c_extensions.extend(files['c_extensions'])
        return python_files, c_extensions

    def build_our_own_python_module(self):
        from .build import build_setup_py, scan_for_files_with_setup_py
        build_setup_py(path.curdir)
        my_files = scan_for_files_with_setup_py(path.curdir, True)
        return my_files['python_files'], my_files['c_extensions']

    def write_pystick_variable_file(self, python_files, c_extensions):
        from .environment import write_pystick_variable_file, get_static_libraries, get_construction_variables
        construction_varilables = get_construction_variables(self.static_libdir, self.options)
        precompiled_static_libs = get_static_libraries(self.static_libdir)
        write_pystick_variable_file(self.pystick_variable_filepath,
                                    python_files, c_extensions,
                                    construction_varilables, precompiled_static_libs)

    @property
    def pystick_variable_filepath(self):
        return path.join(self.embedded_python_build_dir, 'variables.scons')

    @property
    def buildout_directory(self):
        return self.get_buildout_section().get('directory')

    @property
    def isolated_python_dirpath(self):
        return path.join(self.buildout_directory, 'parts', 'python')

    @property
    def embedded_python_build_dir(self):
        return path.join(self.buildout_directory, 'build', 'embedded')

    @property
    def static_libdir(self):
        return path.join(self.buildout_directory, 'build', 'static')

    def get_dependencies_for_embedding(self):
        from ..utils import get_dependencies, get_distributions_from_dependencies
        eggs = self.get_eggs_for_production().split() or [self.get_python_module_name()]
        dependencies = set.union(set(eggs), *[get_dependencies(name) for name in eggs])
        distributions = get_distributions_from_dependencies(dependencies)
        return distributions

    def is_this_a_precompiled_egg_on_windows(self, filepath):
        return system() and filepath.endswith("win-amd64.egg") or filepath.endswith("win32.egg")

    def download_source_instead_of_egg(self, filepath):
        # pyreadline-2.0-py2.7-win-amd64.egg
        package_name, release_version = path.basename(filepath).split('-py').split('-')
        return utils.download_package_source(package_name, self.get_download_cache_dist())

    def iter_archives_for_embedding(self):
        distributions = self.get_dependencies_for_embedding()
        for filepath in glob(path.join(self.get_download_cache_dist(), '*')):
            if path.isdir(filepath):
                continue
            if 'zc.' in filepath:
                continue
            basename = path.basename(filepath).lower()
            exclude_list = self.get_recipe_section().get('exclude_eggs', '').split()
            exclude_matches = [x for x in exclude_list if basename.startswith(x)]
            if exclude_matches:
                logger.info("skipping {} because matched by exclude_eggs rule(s) {!r}".format(basename, exclude_matches))
                continue
            if any([distname.lower() in basename and version.replace('-', '_') in basename.replace('-', '_')
                   for distname, version in distributions.items()]):
                if self.is_this_a_precompiled_egg_on_windows(filepath):
                    filepath = download_source_instead_of_egg(filepath)
                    pass
                yield path.abspath(filepath)


class Executable(Recipe):
    def install(self):
        """:returns: a list of installed filepaths"""
        with self.with_most_mortem():
            python_source_path = self.prepare_sources()
            self.build_embedded_python(python_source_path)
            console_scripts = self.build_console_scripts(python_source_path)
            return console_scripts

    def build_console_scripts(self, python_source_path):
        executables = []
        for executable_name, (module_name, callable_name) in self.get_entry_points_for_production().items():
            executables.append(self.build_console_script(executable_name, module_name, callable_name, python_source_path))
        return executables

    def get_all_entry_points_available_in_production(self):
        from pkg_resources import iter_entry_points
        packages_in_production = self.get_dependencies_for_embedding().keys() + [self.get_python_module_name()]
        return {item.name: (item.module_name, item.attrs[0])
                for item in iter_entry_points('console_scripts')
                if any(item.module_name.startswith(package_name)
                       for package_name in packages_in_production)}

    def get_specific_console_script_names(self):
        return [item.strip() for
                item in self.get_console_scripts_for_production().splitlines() if
                item.strip()]

    def get_entry_points_for_production(self):
        include_dependent_scripts = self.get_dependent_scripts() == 'true'
        package_name = self.get_python_module_name()
        entry_points_dict = {key: value for key, value in self.get_all_entry_points_available_in_production().items()
                             if include_dependent_scripts or value[0].startswith(package_name)}
        specific_script_names = self.get_specific_console_script_names()
        if specific_script_names:
            assert all(item in entry_points_dict for item in specific_script_names)
            return {key: value
                    for key, value in entry_points_dict.items()
                    if key in specific_script_names}
        return entry_points_dict

    def build_console_script(self, executable, module_name, callable_name, python_source_path):
        from .environment import get_sorted_static_libraries
        source = '{}.c'.format(executable)
        cpppath = [path.abspath(path.join(python_source_path, "Include")), self.embedded_python_build_dir]
        libs = [item for item in glob(path.join(self.embedded_python_build_dir, '*fpython*')) if
                not item.endswith('.rsp')]
        libs.extend(get_sorted_static_libraries(self.static_libdir))
        config = 'SConstruct'
        build_dir = path.join('build', 'executables', executable)
        ensure_directory(path.join(build_dir, executable))
        with chdir_context(build_dir):
            with open(source, 'w') as fd:
                fd.write(MAIN.format(executable, module_name, callable_name))
            with open(config, 'w') as fd:
                fd.write(SCONSTRUCT.format(source=source, cpppath=cpppath, libs=libs))
            run_in_another_process(scons, None)
        extension = dict(Windows='.exe').get(system(), '')
        src = path.join(build_dir, executable  + extension)
        dst = path.join('dist', executable + extension)
        ensure_directory(dst)
        copy(src, dst)
        return dst

    def update(self):
        pass


class StaticLibrary(Recipe):
    def install(self):
        """:returns: a list of installed filepaths"""
        with self.with_most_mortem():
            self.build_embedded_python(self.prepare_sources())
            return [self.copy_libfullpython()]

    def copy_libfullpython(self):
        library_name = self.get_python_module_name().split('.')[-1]
        [src] = [item for item in glob(path.join('build', 'embedded', '*fpython*')) if
                 not item.endswith('.rsp')]
        old_library_name = path.basename(src).split('.')[0].replace('lib', '')
        dst = path.join('dist', path.basename(src).replace(old_library_name, library_name))
        ensure_directory(dst)
        copy(src, dst)
        return dst

    def update(self):
        pass
