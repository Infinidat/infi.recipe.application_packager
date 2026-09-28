import os
import unittest

from infi.recipe.application_packager.utils.buildout.windows_bootstrap import (
    _is_buildout_egg_move,
    _rename_with_retry,
)


class FakeClock(object):
    def __init__(self):
        self.value = 0.0
        self.sleeps = []

    def __call__(self):
        return self.value

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.value += seconds


def windows_error(winerror):
    error = OSError('simulated Windows error')
    error.winerror = winerror
    return error


def egg_paths(tmpdir_name='tmp1234'):
    eggs = os.path.abspath('eggs')
    source = os.path.join(eggs, tmpdir_name, 'example-1.0-py3.11.egg')
    destination = os.path.join(eggs, 'example-1.0-py3.11.egg')
    return eggs, source, destination


def call_with_retry(rename, timeout=30, path_exists=lambda unused: False):
    eggs, source, destination = egg_paths()
    clock = FakeClock()
    result = _rename_with_retry(
        source=source,
        destination=destination,
        eggs_directory=eggs,
        timeout=timeout,
        rename=rename,
        sleep=clock.sleep,
        clock=clock,
        path_exists=path_exists,
    )
    return result, clock


class WindowsBootstrapTestCase(unittest.TestCase):

    def test_recognizes_only_buildout_temporary_egg_moves(self):
        eggs, source, destination = egg_paths()
        self.assertTrue(_is_buildout_egg_move(source, destination, eggs))
        self.assertFalse(_is_buildout_egg_move(
            os.path.join(eggs, 'not-temporary', 'example.egg'),
            destination,
            eggs,
        ))
        self.assertFalse(_is_buildout_egg_move(
            source,
            os.path.join(eggs, 'nested', 'example.egg'),
            eggs,
        ))

    def test_retries_transient_windows_errors(self):
        for winerror in (5, 32, 33):
            calls = []

            def rename(source, destination):
                calls.append((source, destination))
                if len(calls) < 3:
                    raise windows_error(winerror)
                return 'renamed'

            result, clock = call_with_retry(rename)

            self.assertEqual(result, 'renamed')
            self.assertEqual(len(calls), 3)
            self.assertEqual(clock.sleeps, [0.05, 0.1])

    def test_does_not_retry_non_transient_errors(self):
        calls = []

        def rename(source, destination):
            calls.append((source, destination))
            raise windows_error(183)

        with self.assertRaises(OSError):
            call_with_retry(rename)

        self.assertEqual(len(calls), 1)

    def test_does_not_retry_if_destination_appeared(self):
        calls = []

        def rename(source, destination):
            calls.append((source, destination))
            raise windows_error(5)

        with self.assertRaises(OSError):
            call_with_retry(rename, path_exists=lambda unused: True)

        self.assertEqual(len(calls), 1)

    def test_stops_retrying_at_timeout(self):
        calls = []

        def rename(source, destination):
            calls.append((source, destination))
            raise windows_error(5)

        with self.assertRaises(OSError):
            call_with_retry(rename, timeout=0.12)

        # Immediate attempt, then retries after 0.05 and 0.07 seconds.
        self.assertEqual(len(calls), 3)

    def test_does_not_retry_rename_outside_the_buildout_egg_move(self):
        eggs, unused_source, destination = egg_paths()
        source = os.path.join(eggs, 'ordinary', 'example.egg')
        calls = []

        def rename(source, destination):
            calls.append((source, destination))
            raise windows_error(5)

        clock = FakeClock()
        with self.assertRaises(OSError):
            _rename_with_retry(
                source=source,
                destination=destination,
                eggs_directory=eggs,
                timeout=30,
                rename=rename,
                sleep=clock.sleep,
                clock=clock,
                path_exists=lambda unused: False,
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(clock.sleeps, [])


if __name__ == '__main__':
    unittest.main()
