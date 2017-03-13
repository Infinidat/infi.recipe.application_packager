from sys import maxsize
from os import path, name, curdir
from gitpy import LocalRepository
from functools import wraps

from logging import getLogger
logger = getLogger(__name__)

def is_64():
    return maxsize() > 2**32

def is_windows():
    return name == 'nt'

def is_executable_exists(filepath):
    return path.exists("{}.exe".format(filepath) if is_windows() else filepath)

def assert_buildout_executable_exists():
    if not is_executable_exists(path.join("bin", "buildout")):
        logger.error("buildout executable does not exist, run `projector devenv build`")
        raise AssertionError()

def assert_setup_py_exists():
    if not path.exists("setup.py"):
        logger.error("setup.py does not exist, run `projector devenv build`")
        raise AssertionError()

def assert_buildout_configfile_exists():
    if not path.exists("buildout.cfg"):
        logger.error("buidlout.cfg does not exist, the current directory is not a home of a project")
        raise AssertionError()

def assert_git_repository():
    if not path.exists(".git"):
        logger.error("the current directory is not a home of a git repository")
        raise AssertionError()

def assert_no_uncommitted_changes():
    repository = LocalRepository(curdir)
    changes = repository.getChangedFiles() + repository.getStagedFiles()
    if changes:
        message = "There are changes pending commit, cannot continue. please commit or checkout those changes:\n"
        logger.error(message+repr(changes))
        raise AssertionError()

def is_isolated_python_exists():
    return path.exists(path.join("parts", "python", "bin",
                                 "python{}".format('.exe' if is_windows() else '')))

def assert_isolated_python_exists():
    if not is_isolated_python_exists():
        logger.error("Isolated python is required")
        raise AssertionError()

def assert_on_branch(branch_name):
    repository = LocalRepository(curdir)
    current_branch = repository.getCurrentBranch()
    if current_branch is None or current_branch.name != branch_name:
        logger.error("not currently on branch {}".format(branch_name))
        raise AssertionError()

def is_buildout_executable_using_isolated_python():
    with open(path.join("bin", "buildout-script.py" if is_windows() else "buildout")) as fd:
        content = fd.read()
    python_abspath = "{}/parts/python/bin/python".format(path.abspath(curdir))
    python_relpath = "parts/python/bin/python"
    shebang_lines = ["#!" + '"{}"'.format(python) if is_windows() else '#!' + python + '-S'
                     for python in [python_relpath, python_abspath]]
    return any([content.startswith(shebang_line) for shebang_line in shebang_lines])

def requires_repository(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        assert_buildout_configfile_exists()
        assert_git_repository()
        return func(*args, **kwargs)
    return decorator

def requires_built_repository(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        assert_buildout_configfile_exists()
        assert_git_repository()
        assert_setup_py_exists()
        return func(*args, **kwargs)
    return decorator
