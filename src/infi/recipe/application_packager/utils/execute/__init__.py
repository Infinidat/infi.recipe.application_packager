from logging import getLogger
from infi.execute import ExecutionError, execute_async

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
