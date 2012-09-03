from logging import getLogger
from infi.execute import ExecutionError

logger = getLogger(__name__)

def execute_assert_success(args, allowed_return_codes=[0], env=None):
    from infi import execute
    logger.info("Executing {}".format(' '.join(args)))
    try:
         pid = execute.execute_assert_success(args, env=env)
         return pid
    except ExecutionError, error:
        return_code = error.result.get_returncode()
        if return_code in allowed_return_codes:
            logger.warning("running {!r} returned {}".format(args, return_code))
            return error.result
        raise

def parse_args(commandline_or_args):
    return commandline_or_args if isinstance(commandline_or_args, list) else commandline_or_args.split()

def _get_executable_from_shebang_line():  # pragma: no cover
    # The executable wrapper in distribute dynamically loads Python's DLL, which causes sys.executable to be the wrapper
    # and not the original python exeuctable. We have to find the real executable as Distribute does.
    from os import path
    import sys
    executable_script_py = sys.executable.replace(".exe", "-script.py")
    with open(executable_script_py) as fd:
        shebang_line = fd.readlines()[0].strip()
    executable_path = path.normpath(shebang_line[3:-1])
    return (executable_path + '.exe') if not executable_path.endswith('.exe') else executable_path

def execute_with_python(commandline_or_args):
    from os import path
    from ...assertions import is_windows
    from infi.recipe.application_packager.scripts import INSTALLDIR
    args = parse_args(commandline_or_args)
    executable = [path.join(INSTALLDIR, 'bin', 'python.exe' if is_windows() else 'python')]
    execute_assert_success(executable + args)

def execute_with_isolated_python(commandline_or_args):
    import sys
    import os
    from ...assertions import is_windows
    args = parse_args(commandline_or_args)
    executable = [os.path.join('parts', 'python', 'bin', 'python{}'.format('.exe' if is_windows() else ''))]
    with open_buildout_configfile() as buildout:
        if buildout.get('buildout', 'relative-paths') in ['True', 'true']:
            [executable] = os.path.abspath(executable[0])
    execute_assert_success(executable + args)
