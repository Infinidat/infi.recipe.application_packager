import argparse
import logging
import math
import os
import sys
import time
import types


logger = logging.getLogger(
    'infi.recipe.application_packager.windows_bootstrap')

TRANSIENT_WINDOWS_RENAME_ERRORS = frozenset((
    5,   # ERROR_ACCESS_DENIED
    32,  # ERROR_SHARING_VIOLATION
    33,  # ERROR_LOCK_VIOLATION
))

INITIAL_RETRY_DELAY = 0.05
MAX_RETRY_DELAY = 1.0


def _normalized_path(path):
    return os.path.normcase(os.path.abspath(path))


def _is_buildout_egg_move(source, destination, eggs_directory):
    source = _normalized_path(source)
    destination = _normalized_path(destination)
    eggs_directory = _normalized_path(eggs_directory)

    source_parent = os.path.dirname(source)
    return (
        os.path.dirname(source_parent) == eggs_directory
        and os.path.dirname(destination) == eggs_directory
        and os.path.basename(source_parent).lower().startswith('tmp')
    )


def _rename_with_retry(source, destination, eggs_directory, timeout,
                       rename, sleep, clock, path_exists):
    if timeout <= 0 or not _is_buildout_egg_move(
            source, destination, eggs_directory):
        return rename(source, destination)

    deadline = clock() + timeout
    delay = INITIAL_RETRY_DELAY
    attempt = 1

    while True:
        try:
            return rename(source, destination)
        except OSError as error:
            winerror = getattr(error, 'winerror', None)
            if winerror not in TRANSIENT_WINDOWS_RENAME_ERRORS:
                raise

            # A destination appearing while we wait is a real collision, not
            # the transient scanner lock this workaround is intended for.
            if path_exists(destination):
                raise

            remaining = deadline - clock()
            if remaining <= 0:
                raise

            sleep_time = min(delay, remaining)
            logger.warning(
                'rename attempt %s failed with WinError %s; '
                'retrying in %.3f seconds: %r -> %r',
                attempt, winerror, sleep_time, source, destination)

            sleep(sleep_time)
            attempt += 1
            delay = min(delay * 2, MAX_RETRY_DELAY)


def install_windows_rename_retry(timeout, eggs_directory):
    if os.name != 'nt' or timeout <= 0:
        return

    import zc.buildout.easy_install as easy_install

    original_rename = os.rename
    clock = getattr(time, 'monotonic', time.time)

    def retrying_rename(source, destination):
        return _rename_with_retry(
            source=source,
            destination=destination,
            eggs_directory=eggs_directory,
            timeout=timeout,
            rename=original_rename,
            sleep=time.sleep,
            clock=clock,
            path_exists=os.path.exists,
        )

    # Do not replace os.rename globally. Functions in easy_install.py resolve
    # their module-level `os` name at runtime, so a private proxy limits the
    # workaround to zc.buildout.easy_install.
    os_proxy = types.ModuleType('os')
    os_proxy.__dict__.update(os.__dict__)
    os_proxy.rename = retrying_rename
    easy_install.os = os_proxy


def _non_negative_finite_float(value):
    value = float(value)
    if value < 0 or math.isnan(value) or math.isinf(value):
        raise argparse.ArgumentTypeError(
            'timeout must be a non-negative finite number')
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '--rename-retry-timeout',
        type=_non_negative_finite_float,
        default=0,
    )
    options, buildout_arguments = parser.parse_known_args(argv)

    install_windows_rename_retry(
        timeout=options.rename_retry_timeout,
        eggs_directory=os.path.join(os.getcwd(), 'eggs'),
    )

    from zc.buildout.buildout import main as buildout_main
    return buildout_main(buildout_arguments)


if __name__ == '__main__':
    result = main()
    if isinstance(result, int):
        sys.exit(result)
