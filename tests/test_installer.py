import infi.unittest as unittest
from infi.os_info import get_platform_string
import infi.recipe.buildout_logging as buildout_logging
import os
import glob
import logging
import shutil

logger = logging.getLogger(__name__)

TESTCASE_DIR = os.path.abspath(os.curdir)
TEST_BUILDOUT = os.path.join(TESTCASE_DIR, 'buildout.cfg')
PACKAGE_NAME = 'infi.recipe.application_packager'
PREFIX = '/opt/infinidat/application-packager'
INSTALLDIR = r"C:\Program Files\Infinidat\Application Packager"
EXTENSION = '.exe' if os.name == 'nt' else ''

def delete_existing_builds():
    items = glob.glob(os.path.join(TESTCASE_DIR, 'parts', '*'))
    for path in filter(lambda path: os.path.isfile(path), items):
        os.remove(path)
    for path in filter(lambda path: os.path.isdir(path), items):
        if path.endswith('python') or path.endswith('buildout') or path.endswith("scripts"):
            continue
        shutil.rmtree(path)

def get_buildout_logs():
    return glob.glob(os.path.join(buildout_logging.LogFileHandler.get_logs_directory(), 'buildout.*'))

def delete_buildout_logs():
    for filepath in get_buildout_logs():
        try:
            os.remove(filepath)
        except:
            pass

def print_buildout_logs():
    for filepath in get_buildout_logs():
        with open(filepath) as fd:
            print fd.read()

def cleanup_buildout_logs():
    print_buildout_logs()
    delete_buildout_logs()

CONSOLE_SCRIPTS = ["hello", "sample", "post_install", "pre_uninstall", "sleep"]

def create_console_scripts():
    from infi.execute import execute_assert_success
    from infi.projector.helper.utils import open_buildout_configfile
    for name in CONSOLE_SCRIPTS:
        with open_buildout_configfile(filepath="buildout.cfg", write_on_exit=True) as buildout:
            scripts = buildout.get("pack", "scripts").split() \
                      if buildout.has_section("pack") and buildout.has_option("pack", "scripts") \
                      else []
            scripts.append(name)
            buildout.set("pack", "scripts", "\n".join(scripts))
        execute_assert_success([os.path.join('bin', 'projector'),
                                "console-scripts", "add", name,
                                "infi.recipe.application_packager.scripts:{0}".format(name),
                                "--commit-changes"])
        execute_assert_success([os.path.join('bin', 'projector'),
                               "devenv", "build", "--no-scripts"])

def create_package():
    from infi.execute import execute_assert_success
    try:
        stderr = execute_assert_success([os.path.join('bin', 'buildout'), '-v', 'install', 'pack']).get_stderr()
        logger.debug('package created, stderr: {}'.format(stderr))
    finally:
        wxs = os.path.join("parts", "product.wxs")
        if os.name == 'nt' and os.path.exists(wxs):
            with open(wxs) as fd:
                print fd.read()

def do_an_empty_commit():
    from gitpy import LocalRepository
    repository = LocalRepository('.')
    repository.commit("TRIVIAL empty commit for testing upgrades", allowEmpty=True)

def devenv_build():
    from infi.execute import execute_assert_success
    execute_assert_success([os.path.join('bin', 'buildout'), '-v', 'install', 'setup.py', '__version__.py'])

def apply_change_in_file(filepath):
    with open(filepath) as fd:
        contents = fd.read()
    with open(filepath, 'w') as fd:
        fd.write(contents.replace('before', 'after'))

def do_a_refactoring_change():
    # HOSTDEV-1781
    from gitpy import LocalRepository
    from os import rename
    scripts_dir = os.path.join("src", "infi", "recipe", "application_packager", "scripts")
    refactoring_dir = os.path.join(scripts_dir, "refactoring")
    scripts_init = os.path.join(scripts_dir, "__init__.py")
    refactoring_py = "{}.py".format(refactoring_dir)
    if not os.path.exists(refactoring_dir):
        return
    # move the file
    rename(os.path.join(refactoring_dir, "__init__.py"), refactoring_py)

    # change the files
    apply_change_in_file(refactoring_py)
    apply_change_in_file(scripts_init)

    # commit the changes
    repository = LocalRepository('.')
    repository.delete(refactoring_dir, recursive=True, force=True)
    repository.add(refactoring_py)
    repository.add(scripts_init)
    repository.commit("HOSTDEV-1781 refactoring scripts/refactoring")

def _apply_close_on_upgrade_or_removal(value):
    from gitpy import LocalRepository
    from infi.recipe.application_packager.utils.buildout import open_buildout_configfile
    with open_buildout_configfile(write_on_exit=True) as buildout:
        buildout.set("pack", "close-on-upgrade-or-removal", value)
    repository = LocalRepository('.')
    repository.add('buildout.cfg')
    repository.commit('HOSTDEV-1922 testing close-on-upgrade-or-removal=false')

def set_close_on_upgrade_or_removal():
    _apply_close_on_upgrade_or_removal('true')

def unset_close_on_upgrade_or_removal():
    _apply_close_on_upgrade_or_removal('false')


from infi.recipe.application_packager.utils.execute import execute_assert_success, execute_async
from infi.recipe.application_packager.utils import chdir
from infi.recipe.application_packager.installer import Installer, MsiInstaller, DebInstaller, RpmInstaller, PkgInstaller

class Base(unittest.TestCase):
    @classmethod
    def should_run(cls):
        return False

    @classmethod
    def setUpClass(cls):
        if not cls.should_run():
            raise unittest.SkipTest("Skipping")
        delete_buildout_logs()
        with chdir(TESTCASE_DIR):
            delete_existing_builds()
            create_console_scripts()
            create_package()

    def setUp(self):
        super(Base, self).setUp()
        self.addCleanup(cleanup_buildout_logs)
        self._chdir_context = chdir(TESTCASE_DIR).__enter__()
        self.assertTrue(self.is_package_exists())
        self._clean_remainings_of_previous_installations()
        self.assert_clean_environment()

    def assert_clean_environment(self):
        self.assertFalse(self.is_product_installed())
        self.assertFalse(self.are_there_remainings_of_previous_installations())
        self.assertFalse(self.has_application_pre_uninstall_script_was_executed())

    def _clean_installation_target_directory(self):
        if os.path.exists(self.targetdir):
            shutil.rmtree(self.targetdir)

    def _clean_dirty_data_of_application_scripts(self):
        pardir = os.path.abspath(os.path.join(self.targetdir, os.path.pardir))
        path = os.path.join(pardir, 'pre_uninstall')
        if os.path.exists(path):
            os.remove(path)

    def _clean_remainings_of_previous_installations(self):
        if self.is_product_installed():
            self.uninstall_package(False)
        self._clean_dirty_data_of_application_scripts()
        self._clean_installation_target_directory()

    def tearDown(self):
        if self._chdir_context is not None:
            self._chdir_context.__exit__()
        super(Base, self).tearDown()

    def has_application_post_install_script_was_executed(self):
        return os.path.exists(os.path.join(self.targetdir, 'post_install'))

    def has_application_pre_uninstall_script_was_executed(self):
        pardir = os.path.abspath(os.path.join(self.targetdir, os.path.pardir))
        return os.path.exists(os.path.join(pardir, 'pre_uninstall'))

    def assert_product_was_installed_successfully(self, with_custom_actions):
        self.assertTrue(self.is_product_installed())
        func = self.assertTrue if with_custom_actions else self.assertFalse
        func(self.has_bootstrap_ocurred())
        func(self.has_application_post_install_script_was_executed())

    def assert_product_was_uninstalled_successfully(self, with_custom_actions):
        self.assertFalse(self.is_product_installed())
        func = self.assertTrue if with_custom_actions else self.assertFalse
        func(self.has_application_pre_uninstall_script_was_executed())
        self.assertFalse(self.are_there_remainings_of_previous_installations())

    @unittest.parameters.iterate("with_custom_actions", [True, False])
    def test_install_and_remove(self, with_custom_actions=True):
        self.assertFalse(self.is_product_installed())
        self.install_package(with_custom_actions)
        self.assert_product_was_installed_successfully(with_custom_actions)
        self.uninstall_package(with_custom_actions)
        self.assert_product_was_uninstalled_successfully(with_custom_actions)

    def test_upgrade(self, with_custom_actions=True):
        self.assertFalse(self.is_product_installed())
        self.install_package(with_custom_actions)
        self.assert_product_was_installed_successfully(with_custom_actions)
        delete_existing_builds()
        do_a_refactoring_change()
        # HOSTDEV-1781
        devenv_build()
        create_package()
        self.install_package(with_custom_actions)
        self.assert_product_was_installed_successfully(with_custom_actions)
        self.uninstall_package(with_custom_actions)
        self.assert_product_was_uninstalled_successfully(with_custom_actions)

    def test_processes_from_previous_version_are_not_killed_during_upgrade(self):
        from time import time, sleep
        if 'windows' in get_platform_string():
            raise unittest.SkipTest("Skipping")
        self.install_package()
        cleanup_buildout_logs()

        # start process
        timeout = 3600
        t0 = time()
        pid = execute_async([os.path.join(self.targetdir, "bin", "sleep" + EXTENSION), str(timeout)])
        # we need to give the process time to start, checking it didn't return 1 because of an error
        sleep(10)
        self.assertFalse(pid.is_finished())

        # upgrade
        delete_existing_builds()
        unset_close_on_upgrade_or_removal()
        do_an_empty_commit()
        devenv_build()
        create_package()
        self.install_package()

        # assert
        cleanup_buildout_logs()
        pid.poll()
        self.assertFalse(pid.is_finished())

    def test_processes_from_previous_version_are_killed_during_upgrade(self):
        from time import time, sleep
        self.install_package()
        cleanup_buildout_logs()

        # start process
        timeout = 3600
        t0 = time()
        pid = execute_async([os.path.join(self.targetdir, "bin", "sleep" + EXTENSION), str(timeout)])
        # we need to give the process time to start, checking it didn't return 1 because of an error
        sleep(10)
        self.assertFalse(pid.is_finished())

        # upgrade
        delete_existing_builds()
        set_close_on_upgrade_or_removal()
        do_an_empty_commit()
        devenv_build()
        create_package()
        self.install_package()

        # assert
        cleanup_buildout_logs()
        pid.poll()
        self.assertTrue(pid.is_finished())
        self.assertLess(time(), t0 + timeout)

    @classmethod
    def platform_specific_cleanup(cls):
        raise NotImplementedError()


class MsiTestCase(Base, MsiInstaller):
    def __init__(self, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)
        MsiInstaller.__init__(self, TEST_BUILDOUT)

    @classmethod
    def platform_specific_cleanup(cls):
        if os.path.exists(INSTALLDIR):
            shutil.rmtree(INSTALLDIR)

    @classmethod
    def should_run(cls):
        return 'windows' in get_platform_string()


class Posix(Base):
    pass


class RpmTestCase(Posix, RpmInstaller):
    def __init__(self, *args, **kwargs):
        Posix.__init__(self, *args, **kwargs)
        RpmInstaller.__init__(self, TEST_BUILDOUT)

    @classmethod
    def platform_specific_cleanup(cls):
        env = os.environ.copy()
        env['NO_CUSTOM_ACTIONS'] = '1'
        execute_assert_success(['rpm', '-e', PACKAGE_NAME, '--noscripts'], env=env, allowed_return_codes=[0, 1, 2])

    @classmethod
    def should_run(cls):
        return 'redhat' in get_platform_string() or 'centos' in get_platform_string()


class DebTestCase(Posix, DebInstaller):
    def __init__(self, *args, **kwargs):
        Posix.__init__(self, *args, **kwargs)
        DebInstaller.__init__(self, TEST_BUILDOUT)

    @classmethod
    def platform_specific_cleanup(cls):
        env = os.environ.copy()
        env['NO_CUSTOM_ACTIONS'] = '1'
        execute_assert_success(['dpkg', '-r', PACKAGE_NAME], env=env, allowed_return_codes=[0, 1, 2])

    @classmethod
    def should_run(cls):
        return 'ubuntu' in get_platform_string() or 'debian' in get_platform_string()


class PkgTestCase(Posix, PkgInstaller):
    def __init__(self, *args, **kwargs):
        Posix.__init__(self, *args, **kwargs)
        PkgInstaller.__init__(self, TEST_BUILDOUT)

    @classmethod
    def platform_specific_cleanup(cls):
        env = os.environ.copy()
        env['NO_CUSTOM_ACTIONS'] = '1'
        execute_assert_success(['pkgrm', '-n', PACKAGE_NAME], env=env, allowed_return_codes=[0,])

    @classmethod
    def should_run(cls):
        return 'solaris' in get_platform_string()
