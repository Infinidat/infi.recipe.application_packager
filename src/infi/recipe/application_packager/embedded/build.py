from glob import glob
from json import loads
from zipfile import ZipFile
from os import path, name, makedirs, remove, environ
from pkg_resources import resource_string, ensure_directory
from infi.execute import execute_assert_success
from infi.recipe.application_packager.utils import chdir as chdir_context
from logging import getLogger

logger = getLogger(__name__)
SETUP_PY_MOCK = resource_string('infi.recipe.application_packager.embedded', 'setup.py').decode('ascii')
PYTHON_SCRIPT = path.abspath(path.join(path.curdir, 'bin', 'python'))
PYTHON_EXECUTABLE = path.abspath(path.join(path.curdir, 'parts', 'python', 'bin', 'python'))


def build_setup_py(dirname):
    # we want to really build the package by running setup.py
    # so any code generation would take place (for example, Cython to C code)
    # we specify the curent directory as the build-temp directory so all the generated sources
    # will be in the same directory as the other python code
    with chdir_context(dirname):
        env = environ.copy()
        env.update(PYTHONPATH=path.abspath(path.curdir))
        cmd = [PYTHON_EXECUTABLE, PYTHON_SCRIPT, 'setup.py', 'build', '--build-temp=.'] if name != 'nt' else \
              [PYTHON_SCRIPT, 'setup.py', 'build', '--build-temp=.']
        logger.info(' '.join(cmd))
        pid = execute_assert_success(cmd, env=env)
        logger.debug(pid.get_stdout() + pid.get_stderr())


def _unzip_egg(filepath):
    basename = path.basename(filepath)
    dirname = basename.rsplit('-', 1)[0]
    if path.exists(dirname):
        return dirname
    if not path.exists(dirname):
        makedirs(dirname)
    with open(filepath, 'rb') as fd:
        archive = ZipFile(fd, 'r')
        archive.extractall(dirname)
    return dirname


def _extract_and_build_zip(filepath):
    basename = path.basename(filepath)
    dirname = basename.rsplit('.', 1)[0]
    with open(filepath, 'rb') as fd:
        archive = ZipFile(fd, 'r')
        archive.extractall()
    build_setup_py(dirname)
    return dirname


def _extract_and_build_tgz(filepath):
    import tarfile
    basename = path.basename(filepath)
    dirname = basename.rsplit('.', 2)[0]
    if path.exists(dirname):
        return dirname
    archive = tarfile.open(filepath, 'r:gz')
    archive.extractall()
    archive.close()
    build_setup_py(dirname)
    return dirname


def build_dependency(filepath):
    """:returns: base directory"""
    build_dir = path.abspath(path.join('build', 'dependencies'))
    ensure_directory(path.join(build_dir, 'x'))
    with chdir_context(build_dir):
        basename = path.basename(filepath)
        logger.info("building {}".format(basename))
        if basename.endswith('egg'):
            # we assume that all the egg sources are pure-python and don't contain binaries
            # people obviosuly don't upload binary eggs for POSIX systems to PyPI
            # but on Windows they do, and therefore we already downloaded their source districutions
            # in a previous step in the build process of the recipe
            return path.join(build_dir, _unzip_egg(filepath))
        elif basename.endswith('zip'):
            return path.join(build_dir, _extract_and_build_zip(filepath))
        elif basename.endswith('gz'):
            return path.join(build_dir, _extract_and_build_tgz(filepath))
        else:
            raise RuntimeError()


def scan_for_files_with_setup_py(build_dir, cleanup=False):
    from . import setup
    python_files, c_extensions = [], []
    with chdir_context(build_dir):
        setup_py_mock = "_embed_recipe.py"
        setup_py_mock_json = "_embed_recipe.json"
        if not path.exists(setup_py_mock_json):
            with open(setup_py_mock, 'w') as fd:
                fd.write(SETUP_PY_MOCK)
            env = environ.copy()
            env.update(PYTHONPATH=path.abspath(path.curdir))
            cmd = [PYTHON_EXECUTABLE, PYTHON_SCRIPT, setup_py_mock, 'build'] if name != 'nt' else \
                  [PYTHON_SCRIPT, setup_py_mock, 'build']
            logger.info(' '.join(cmd))
            pid = execute_assert_success(cmd, env=env)
            logger.debug(pid.get_stdout() + pid.get_stderr())
        with open(setup_py_mock_json) as fd:
            files = loads(fd.read())
        if cleanup:
            remove(setup_py_mock)
            remove(setup_py_mock_json)
        return files


def _scan_egg_dir(build_dir):
    # there can be several stuff inside an extracted egg
    # <package>-<version>-py27.egg/
    #   EGG-INFO/
    #   <package>/
    from .setup import scan_for_python_files
    python_files = []

    # read package name
    with open(path.join(build_dir, "EGG-INFO", "top_level.txt"), "rb") as f:
        package_name = f.read().strip()

    package_as_py_file_path = path.join(build_dir, "{}.py".format(package_name))
    if path.isfile(package_as_py_file_path):
        return dict(python_files=[dict(package=False, name=package_name, source=package_as_py_file_path)],
                    c_extensions=[])

    for dirpath in glob(path.join(build_dir, '*')):
        if not path.isdir(dirpath):
            continue
        if not path.basename(dirpath) in build_dir:
            continue
        python_files.extend(scan_for_python_files(dirpath, path.basename(dirpath)))
    return dict(python_files=python_files, c_extensions=[])


def scan_for_files(build_dir):
    """:returns: dict of python_files, c_extenstions"""
    logger.info("scanning {}".format(build_dir))
    if path.exists(path.join(build_dir, 'setup.py')):
        return scan_for_files_with_setup_py(build_dir)
    return _scan_egg_dir(build_dir)
