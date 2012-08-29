import unittest
import sys
import mock

class Ubuntu(object):
    @staticmethod
    def system():
        return 'Linux'

    @staticmethod
    def linux_distribution():
        return ("Ubuntu", "12.04", '')

class Redhat(object):
    @staticmethod
    def system():
        return 'Linux'

    @staticmethod
    def linux_distribution():
        return ("Red Hat Enterprise Linux Server", "6.1", '')

class Windows(object):
    @staticmethod
    def system():
        return 'Windows'

def cleanup_sys_argv():
    argv = sys.argv
    def cleanup():
        sys.argv=argv
    return cleanup

from . import long_one


class PackWithMockTestCase(unittest.TestCase):
    @long_one
    def test_pack_deb(self):
        with mock.patch("infi.recipe.application_packager.utils.execute.execute_assert_success") as execute_assert_success:
            with mock.patch("infi.recipe.application_packager.utils.compiler.compile_binary_distributions"):
                with mock.patch("platform.system", new=Ubuntu.system), \
                     mock.patch("platform.linux_distribution", new=Ubuntu.linux_distribution) as linux_distribution:
                    with mock.patch("shutil.copy"), mock.patch("shutil.rmtree"):
                        self.addCleanup(cleanup_sys_argv())
                        sys.argv = ['buildout', 'buildout:develop=.', 'install', 'pack']
                        from zc.buildout.buildout import main
                        main()
                        # TODO add assertions

    @long_one
    def test_pack_rpm(self):
        with mock.patch("infi.recipe.application_packager.utils.execute.execute_assert_success") as execute_assert_success:
            with mock.patch("infi.recipe.application_packager.utils.compiler.compile_binary_distributions"):
                with mock.patch("platform.system", new=Redhat.system), \
                     mock.patch("platform.linux_distribution", new=Redhat.linux_distribution) as linux_distribution:
                    with mock.patch("shutil.copy"), mock.patch("shutil.rmtree"):
                        with mock.patch("re.search"):
                            self.addCleanup(cleanup_sys_argv())
                            sys.argv = ['buildout', 'buildout:develop=.', 'install', 'pack']
                            from zc.buildout.buildout import main
                            main()
                            # TODO add assertions
    @long_one
    def test_pack_msi(self):
        with mock.patch("infi.recipe.application_packager.utils.execute.execute_assert_success") as execute_assert_success:
                with mock.patch("platform.system", new=Windows.system):
                    with mock.patch("shutil.copy"), mock.patch("shutil.rmtree"):
                        self.addCleanup(cleanup_sys_argv())
                        sys.argv = ['buildout', 'buildout:develop=.', 'install', 'pack']
                        from zc.buildout.buildout import main
                        main()
                        # TODO add assertions
