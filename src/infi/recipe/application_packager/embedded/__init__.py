__import__("pkg_resources").declare_namespace(__name__)

from infi.recipe.application_packager.utils import chdir as chdir_context
from infi.recipe.application_packager.base import PackagingRecipe
from pkg_resources import resource_string, ensure_directory, resource_filename
from infi.execute import execute_assert_success
from logging import getLogger
from platform import system
from shutil import copy
from glob import glob
from os import path, name as os_name

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
    sys.argv = ['scons'] + (args or list())
    Script.main()


def run_in_another_process(target, args):
    # scons uses a lot of global variables, makes it impossible to run two difference
    # scons files under the same processes
    from .environment import is_64bit
    from os import name, environ
    from multiprocessing import Process
    if name == 'nt':
        # although we bypass the MSVC batch script detection and specific the target architecture,
        # this is still needed for SCons to run
        environ['PROCESSOR_ARCHITECTURE'] = "AMD64" if is_64bit() else "x86"
    process = Process(target=target, args=(args,))
    process.start()
    process.join()
    if process.exitcode > 0:
        raise RuntimeError(process.exitcode)


class Recipe(PackagingRecipe):
    def should_always_build(self):
        return self.get_recipe_section().get('always-build', 'false') == 'true'

    def prepare_sources(self):
        """
        downloads Python source, setuptools and zc.build prepare_sources to .cache/dist
        :returns: path of extracted Python source
        """
        from . import python_source
        from .. import utils
        assert path.exists(self.isolated_python_dirpath)
        utils.download_buildout(self.get_download_cache_dist())
        utils.download_setuptools(self.get_download_cache_dist())
        return python_source.get_python_source(self.buildout, self.options)

    def build_embedded_python(self, python_source_path):
        artifacts = [f for f in glob(path.join(self.embedded_python_build_dir, '*fpython*')) if not f.endswith('.rsp')]
        if artifacts and not self.should_always_build():
            logger.debug("embedded python is already built, skipping it")
            return
        self.prepare_for_running_pystick()
        args = ["PYTHON_SOURCE_PATH={}".format(python_source_path),
                "BUILD_PATH={}".format(self.embedded_python_build_dir),
                "--defaultenv={}".format(self.pystick_variable_filepath)]
        run_in_another_process(pystick, args)

    def prepare_for_running_pystick(self):
        if path.exists(self.pystick_variable_filepath) and not self.should_always_build():
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
        from .environment import write_pystick_variable_file, get_scons_variables
        construction_varilables = get_scons_variables(self.static_libdir, self.options)
        write_pystick_variable_file(self.pystick_variable_filepath,
                                    python_files, c_extensions,
                                    construction_varilables)

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
        from .. import utils
        package_name, release_version = path.basename(filepath).split('-py')[0].split('-')
        dirpath = self.get_download_cache_dist()
        basename = utils.download_package_source(package_name, dirpath)
        return path.join(dirpath, basename)

    def iter_archives_for_embedding(self):
        distributions = self.get_dependencies_for_embedding()
        for filepath in glob(path.join(self.get_download_cache_dist(), '*')):
            if path.isdir(filepath):
                continue
            if 'zc.' in filepath:
                continue
            basename = path.basename(filepath).lower()
            exclude_list = self.get_recipe_section().get('exclude-eggs', '').split()
            exclude_matches = [x for x in exclude_list if basename.startswith(x)]
            if exclude_matches:
                logger.info("skipping {} because matched by exclude_eggs rule(s) {!r}".format(basename, exclude_matches))
                continue
            if any([distname.lower() in basename and version.replace('-', '_') in basename.replace('-', '_')
                   for distname, version in distributions.items()]):
                if self.is_this_a_precompiled_egg_on_windows(filepath):
                    filepath = self.download_source_instead_of_egg(filepath)
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
        """
        returns a dict of all the 'console_scripts' entry points from:
        * all the packages mentioned in the 'egg's propety
        * all the scripts declared in the packaged setup.py script
        :returns: a script_name: (module_name, callable_name) dictionary
        """
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
        """
        returns a dictionary of all the console script we need to create an executable for
        this method implements the same behavior as infi.recipe.console_scripts for generating scripts:
        * console scripts are searched in the following packages:
        ** in all the packages defined in the 'eggs' property, which by default contains ${project:name}
        * by default, all the console-script entry points that are found by the logic above. unless:
        ** the recipe has a 'scripts' property, and in this case only the script names mentioned in it are generated
        :returns: a script_name: (module_name, callable_name) dictionary
        """
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
        def generate_executable_c_code():
            source_filename = '{}.c'.format(executable)
            with open(source_filename, 'wb') as fd:
                fd.write(MAIN.format(executable, module_name, callable_name))
            return source_filename

        def generate_buildsystem_for_the_executable(source_filename):
            # we need to use the same build environment we used to build the embedded python interpreter
            # and add some stuff on top of it
            from .environment import write_pystick_variable_file, get_sorted_static_libraries, get_scons_variables
            from .environment import is_64bit
            from pprint import pformat
            variables = get_scons_variables(self.static_libdir, self.options)
            # linkking with fpython
            variables['LIBPATH'].insert(0, self.embedded_python_build_dir)
            variables['LIBS'].insert(0, 'fpython27')
            # our generated C code for main uses headers from the Python source code
            variables['CPPFLAGS'] += ' -I{}'.format(self.embedded_python_build_dir)
            variables['CPPFLAGS'] += ' -I{}'.format(path.join(python_source_path, 'Include'))
            variables['CPPDEFINES'] = ["Py_BUILD_CORE"]
            manifest = resource_filename(__name__, 'Microsoft.VC90.CRT.manifest-{}'.format('x64' if is_64bit() else 'x86'))
            manifest_embedded = "'mt.exe -nologo -manifest {} -outputresource:$TARGET;2'".format(manifest)

            with open('SConstruct', 'w') as fd:
                fd.write(SCONSTRUCT.format(source=source_filename, variables=pformat(variables, indent=4),
                                           manifest="LINKCOM=[env['LINKCOM'], {}]".format(manifest_embedded)
                                           if os_name == 'nt' else ''))

        def compile_code_and_link_with_static_library():
            run_in_another_process(scons, None)

        def copy_executable_to_dist():
            extension = dict(Windows='.exe').get(system(), '')
            src = path.join(build_dir, executable  + extension)
            dst = path.join('dist', executable + extension)
            ensure_directory(dst)
            copy(src, dst)
            return dst

        build_dir = path.join('build', 'executables', executable)
        ensure_directory(path.join(build_dir, executable))
        with chdir_context(build_dir):
            source_filename = generate_executable_c_code()
            generate_buildsystem_for_the_executable(source_filename)
            compile_code_and_link_with_static_library()
            run_in_another_process(scons, None)
        dst = copy_executable_to_dist()
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
        # libfpython already includes all the added python moduels and c extensions, no need to compile anyting
        # we just copy the modules to dist/ with a proper name
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
