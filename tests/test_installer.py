import infi.unittest as unittest
import os
import glob
import logging
import shutil
import platform

logger = logging.getLogger(__name__)

TESTCASE_DIR = os.path.abspath(os.curdir)
TEST_BUIILDOUT = os.path.join(TESTCASE_DIR, 'buildout.cfg')
PACKAGE_NAME = 'infi.recipe.application_packager'
PREFIX = '/opt/infinidat/application-packager'
INSTALLDIR = r"C:\Program Files\Infinidat\Application Packager"

def delete_existing_builds():
    items = glob.glob(os.path.join(TESTCASE_DIR, 'parts', '*'))
    for path in filter(lambda path: os.path.isfile(path), items):
        os.remove(path)
    for path in filter(lambda path: os.path.isdir(path), items):
        if path.endswith('python') or path.endswith('buildout') or path.endswith("scripts"):
            continue
        shutil.rmtree(path)

CONSOLE_SCRIPTS = ["hello", "sample", "post_install", "pre_uninstall", "sleep"]

def create_console_scripts():
    from infi.execute import execute_assert_success
    from infi.projector.helper.utils import open_buildout_configfile
    for name in CONSOLE_SCRIPTS:
        with open_buildout_configfile(filepath="buildout.cfg", write_on_exit=True) as buildout:
            scripts = buildout.get("pack", "scripts").split()
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
    execute_assert_success([os.path.join('bin', 'buildout'), '-v', 'install', 'pack'])

def do_an_empty_commit():
    from gitpy import LocalRepository
    repository = LocalRepository('.')
    repository.commit("TRIVIAL empty commit for testing upgrades", allowEmpty=True)

def devenv_build():
    from infi.execute import execute_assert_success
    execute_assert_success([os.path.join('bin', 'buildout'), '-v', 'install', 'setup.py', '__version__.py'])

from infi.recipe.application_packager.utils.execute import execute_assert_success
from infi.recipe.application_packager.utils import chdir
from infi.recipe.application_packager.installer import Installer, MsiInstaller, DebInstaller, RpmInstaller

class Base(unittest.TestCase):
    @classmethod
    def should_run(cls):
        return False

    @classmethod
    def setUpClass(cls):
        if not cls.should_run():
            raise unittest.SkipTest("Skipping")
        with chdir(TESTCASE_DIR):
            delete_existing_builds()
            create_console_scripts()
            create_package()

    def setUp(self):
        super(Base, self).setUp()
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

    @unittest.parameters.iterate("with_custom_actions", [True, False])
    def test_upgrade(self, with_custom_actions=True):
        self.assertFalse(self.is_product_installed())
        self.install_package(with_custom_actions)
        self.assert_product_was_installed_successfully(with_custom_actions)
        delete_existing_builds()
        do_an_empty_commit()
        devenv_build()
        create_package()
        self.install_package(with_custom_actions)
        self.assert_product_was_installed_successfully(with_custom_actions)
        self.uninstall_package(with_custom_actions)
        self.assert_product_was_uninstalled_successfully(with_custom_actions)

    @classmethod
    def platform_specific_cleanup(cls):
        raise NotImplementedError()

class MsiTestCase(Base, MsiInstaller):
    def __init__(self, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)
        MsiInstaller.__init__(self, TEST_BUIILDOUT)

    @classmethod
    def platform_specific_cleanup(cls):
        if os.path.exists(INSTALLDIR):
            shutil.rmtree(INSTALLDIR)

    @classmethod
    def should_run(cls):
        return platform.system() == "Windows"

class Posix(Base):
    pass

class RpmTestCase(Posix, RpmInstaller):
    def __init__(self, *args, **kwargs):
        Posix.__init__(self, *args, **kwargs)
        RpmInstaller.__init__(self, TEST_BUIILDOUT)

    @classmethod
    def platform_specific_cleanup(cls):
        env = os.environ.copy()
        env['NO_CUSTOM_ACTIONS'] = '1'
        execute_assert_success(['rpm', '-e', PACKAGE_NAME, '--noscripts'], env=env, allowed_return_codes=[0, 1, 2])

    @classmethod
    def should_run(cls):
        return platform.system() == "Linux" and platform.linux_distribution()[0].lower().startswith('red')

class DebTestCase(Posix, DebInstaller):
    def __init__(self, *args, **kwargs):
        Posix.__init__(self, *args, **kwargs)
        DebInstaller.__init__(self, TEST_BUIILDOUT)

    @classmethod
    def platform_specific_cleanup(cls):
        env = os.environ.copy()
        env['NO_CUSTOM_ACTIONS'] = '1'
        execute_assert_success(['dpkg', '-r', PACKAGE_NAME], env=env, allowed_return_codes=[0, 1, 2])

    @classmethod
    def should_run(cls):
        return platform.system() == "Linux" and platform.linux_distribution()[0].lower()[0:3] in ['ubu', 'deb']
