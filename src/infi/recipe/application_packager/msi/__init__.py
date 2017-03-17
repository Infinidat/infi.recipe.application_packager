__import__("pkg_resources").declare_namespace(__name__)

from logging import getLogger
from infi.recipe.application_packager.base import PackagingRecipe, RECIPE_DEFAULTS
from infi.recipe.application_packager import utils, assertions
from os import path, curdir, makedirs, listdir
from shutil import rmtree, copy
from pkg_resources import resource_filename
from contextlib import contextmanager

logger = getLogger(__name__)

BYPASS_CUSTOM_ACTION_PROPERTY = "NO_CUSTOM_ACTIONS"
CONDITION_DURING_INSTALL_OR_REPAIR = 'NOT Installed OR MaintenanceMode="Modify"'
CONDITION_DURING_UNINSTALL_NOT_UPGRADE = 'REMOVE="ALL" AND NOT UPGRADINGPRODUCTCODE'
CONDITION_DURING_UPGRADE = "UPGRADINGPRODUCTCODE"
CONDITION_DURING_UPGRADE_AND_UNINSTALL = "({}) OR ({})".format(CONDITION_DURING_UPGRADE, CONDITION_DURING_UNINSTALL_NOT_UPGRADE)
LAUNCH_CONDITION__WINDOWS_2008_AND_R2_ONLY = \
    "(Not Version9X) And (Not VersionNT=400) And (Not VersionNT=500) And (Not VersionNT=501) And" + \
    "(Not VersionNT=502) And (Not (VersionNT=600 And (MsiNTProductType=1))) And " + \
    "(Not (VersionNT=601 And (MsiNTProductType=1)))"
OS_REQUIREMENTS_LAUNCH_CONDITION_MESSAGE = "The operating system is not adequate for running [ProductName]."
OS_32BIT_ON_64BIT_LAUNCH_CONDITION_MESSAGE = "[ProductName] installation on a 64-bit operating system requires the 64-bit installation package. Please get the 64-bit package and try again."
OPERATING_SYSTEMS = {
                     # OS Name: (allow-install, condition)
                     "Windows 10": (False, '(VersionNT=603 And WindowsBuild>="9600" And (MsiNTProductType=1))'),
                     "Windows Server 2016": (True, '(VersionNT=603 And WindowsBuild>="9600" And (MsiNTProductType=2 Or MsiNTProductType=3))'),
                     "Windows 8.1": (False, '(VersionNT=603 And WindowsBuild<"9600" And (MsiNTProductType=1))'),
                     "Windows Server 2012 R2": (True, '(VersionNT=603 And WindowsBuild<"9600" And (MsiNTProductType=2 Or MsiNTProductType=3))'),
                     "Windows Server 2012": (True, '(VersionNT=602 And (MsiNTProductType=2 Or MsiNTProductType=3))'),
                     "Windows 8": (False, '(VersionNT=602 And (MsiNTProductType=1))'),
                     "Windows Server 2008 R2": (True,
                                                '(VersionNT=601 And (MsiNTProductType=2 Or MsiNTProductType=3))'),
                     "Windows Server 2008": (True,
                                             '(VersionNT=600 And (MsiNTProductType=2 Or MsiNTProductType=3))'),
                     "Windows Server 2003": (False, '(VersionNT=502)'),
                     "Windows 7": (False, '(VersionNT=601 And (MsiNTProductType=1))'),
                     "Windows Vista": (False, '(VersionNT=600 And (MsiNTProductType=1))'),
                     "Windows XP": (False, '(VersionNT=501)'),
                     "Windows 2000": (False, '(VersiontNT=500)'),
                     "Windows 98": (False, '(Version9X)'),
                     "Windows NT4": (False, '(VersionNT=400)'),
                    }

SILENT_LAUNCHER = "silent_launcher-{}.exe"

class Recipe(PackagingRecipe):
    def install(self):
        with self.with_most_mortem():
            self.delete_non_production_packages_from_cache_dist()
            self.signtool = self.get_signtool()
            self.write_get_pip_for_production()
            self.write_buildout_configuration_file_for_production()

            # its true we have pre-compiled eggs for Windows
            # but we need to deal with pure-python packages that use setup_requires
            # and specifically pbr
            utils.compiler.byte_compile_lib(self.get_buildout_dir())
            self.download_python_packages_used_by_packaging()
            silent_launcher = self.get_silent_launcher()
            if self.get_add_remove_programs_icon() and not self.icons_already_set():
                self.set_icon_in_all_executables_in_project()
                utils.rcedit.set_icon_in_executable(silent_launcher, self.get_add_remove_programs_icon())
                self.mark_icons_set()
            if self.should_sign_files() and not self.already_signed():
                self.sign_all_executables_in_project()
                self.signtool.sign_file(silent_launcher)
                self.mark_signed()
            utils.compiler.compile_binary_distributions(self.get_buildout_dir(),
                                                        self.get_download_cache_dist(),
                                                        self.get_eggs_directory(),
                                                        self.using_wheels())
            self.convert_python_packages_used_by_packaging_to_wheels()
            package = self.build_package(silent_launcher)
            logger.debug("Built {}".format(package))
            if self.should_sign_files():
                self.signtool.sign_file(package)
                logger.debug("Signed {}".format(package))
            return [package, ]

    def _touch(self, filepath):
        with open(filepath, 'w'):
            pass

    def mark_icons_set(self):
        self._touch(path.join(self.get_download_cache(), 'icons-added'))

    def mark_signed(self):
        self._touch(path.join(self.get_download_cache(), 'executables-signed'))

    def icons_already_set(self):
        return path.exists(path.join(self.get_download_cache(), 'icons-added'))

    def already_signed(self):
        return path.exists(path.join(self.get_download_cache(), 'executables-signed'))

    def get_silent_launcher(self):
        from tempfile import mkstemp
        from shutil import copy
        from os import close
        fd, abspath = mkstemp()
        close(fd)
        launcher = resource_filename(__name__, SILENT_LAUNCHER.format(self.get_platform_arch()))
        copy(launcher, abspath)
        return abspath

    def sign_all_executables_in_project(self):
        for archive_path in self.glob_in_dist_directory("setuptools*"):
            self.signtool.sign_executables_in_archive(archive_path)
        for archive_path in self.glob_in_dist_directory("infi.recipe.console_scripts*"):
            self.signtool.sign_executables_in_archive(archive_path)
        for archive_path in self.glob_in_dist_directory("infi.node_webkit*"):
            self.signtool.sign_executables_in_archive(archive_path)
        # The original python executable is running, cannot sign it
        # self.signtool.sign_file(path.join(self.get_buildout_dir(), 'parts', 'python', 'bin', 'python.exe'))

    def set_icon_in_all_executables_in_project(self):
        icon = self.get_add_remove_programs_icon()
        for archive_path in self.glob_in_dist_directory("setuptools*"):
            utils.rcedit.set_icon_for_executables_in_archive(archive_path, icon)
        for archive_path in self.glob_in_dist_directory("infi.recipe.console_scripts*"):
            utils.rcedit.set_icon_for_executables_in_archive(archive_path, icon)

    def glob_in_dist_directory(self, basename):
        from glob import glob
        return glob(path.abspath(path.join(self.get_download_cache_dist(), basename)))

    def write_wix_to_destination_directory(self, wix):
        import xml.etree.ElementTree as ET
        src = path.join(self.get_working_directory(), 'product.wxs')
        with open(src, 'w') as fd:
            fd.write(wix.to_xml())
        return src

    def build_package(self, silent_launcher):
        wix = self.prepare_wix(silent_launcher)
        wix_filepath = self.write_wix_to_destination_directory(wix)
        with self.wix_context() as wix_basedir:
            wix.build(wix_basedir, wix_filepath, self.get_msi_filepath())
        return self.get_msi_filepath()

    def prepare_wix(self, silent_launcher):
        from .wix import Wix
        recipe = self.get_recipe_section()
        existing_installdir = recipe.get("existing-installdir")
        custom_installdir = recipe.get("custom-installdir")
        wix = Wix(self.get_product_name(), self.get_project_version__short(),
                  self.get_platform_arch(), self.get_upgrade_code(), self.get_description(),
                  self.get_company_name(), self.get_documentation_url(), self.get_add_remove_programs_icon(),
                  existing_installdir, custom_installdir)
        silent_launcher_file_id = self._put_all_files(wix, silent_launcher)
        self._append_bindir_to_system_path(wix)
        self._append_custom_actions(wix, silent_launcher_file_id)
        self._add_launch_conditions(wix)
        self._add_project_entry_points(wix, silent_launcher_file_id)
        self._add_shortcuts(wix)
        banner_bmp = self.get_msi_banner_bmp()
        if banner_bmp:
            logger.info("Setting custom banner {}".format(banner_bmp))
            wix.add_variable("WixUIBannerBmp", banner_bmp)
        dialog_bmp = self.get_msi_dialog_bmp()
        if dialog_bmp:
            logger.info("Setting custom dialog {}".format(dialog_bmp))
            wix.add_variable("WixUIDialogBmp", dialog_bmp)
        eula = self.get_eula_rtf()
        if eula:
            logger.info("Setting custom eula {}".format(eula))
            wix.add_variable("WixUILicenseRtf", eula)
        return wix

    @contextmanager
    def wix_context(self):
        from zipfile import ZipFile
        with utils.temporary_directory_context() as tempdir:
            wix_archive = self.get_wix35_binaries_zip_from_the_internet()
            with open(wix_archive, 'rb') as fd:
                archive = ZipFile(fd, 'r')
                archive.extractall(tempdir)
            yield tempdir

    def get_wix35_binaries_zip_from_the_internet(self):
        from urllib import urlretrieve
        from tempfile import mkstemp
        from os import close
        fd, path = mkstemp(suffix='.zip')
        close(fd)
        urlretrieve("http://python.infinidat.com/packages/main-stable/index/packages/wix/releases/3.5/distributions/other/architectures/x86/extensions/zip/wix-3.5-windows-x86.zip", path)
        return path

    def _append_bindir_to_system_path(self, wix):
        from .wix import generate_guid
        bindir = wix.mkdir('bin', wix.installdir)
        assembly_dir = wix.mkdir('Microsoft.VC90.CRT', bindir)
        component = wix.new_component(wix.new_id('bin'), bindir, generate_guid())
        wix.add_environment_variable('Path', r'[INSTALLDIR]bin', component)

    def _put_all_files(self, wix, silent_launcher):
        wix.add_file('get-pip.py', wix.installdir)
        wix.add_file('buildout.in', wix.installdir, 'buildout.cfg')
        wix.add_file('setup.py', wix.installdir)
        cachedir = wix.mkdir('.cache', wix.installdir)
        silent_launcher_file_id = wix.add_file(silent_launcher, cachedir).id
        develop_eggs = wix.mkdir('develop-eggs', wix.installdir)
        wix.add_directory(self.get_download_cache_dist(), cachedir)
        parts = wix.mkdir('parts', wix.installdir)
        wix.mkdir('buildout', parts)
        wix.mkdir('production-scripts', parts)
        wix.add_directory(path.join(self.get_buildout_dir(), 'parts', 'python'), parts, include_pyc=True)
        wix.add_directory(path.join(self.get_buildout_dir(), 'src'), wix.installdir)
        wix.add_directory(path.join(self.get_buildout_dir(), 'eggs'), wix.installdir, True, True)
        self.add_aditional_directories()
        return silent_launcher_file_id

    def _append_os_removedirs_eggs(self, wix, silent_launcher_file_id):
        commandline = r'''"[INSTALLDIR]parts\python\bin\python.exe" -c "from shutil import rmtree; rmtree('eggs', True)"'''
        action = wix.add_deferred_in_system_context_custom_action('os_removedirs_eggs', commandline,
                                                                  condition=CONDITION_DURING_INSTALL_OR_REPAIR,
                                                                  silent_launcher_file_id=silent_launcher_file_id,
                                                                  text="Removing temporary egg directories, this may take a few minutes")
        return action.id

    def _append_get_pip_custom_action(self, wix, os_removedirs_eggs_id, silent_launcher_file_id):
        commandline = r'"[INSTALLDIR]parts\python\bin\python.exe" get-pip.py ' + \
                      r'--force-reinstall --ignore-installed --upgrade --isolated --no-index ' + \
                      r'--find-links .cache\dist ' + \
                      r'pip setuptools zc.buildout buildout.wheel pythonpy'
        action = wix.add_deferred_in_system_context_custom_action('get-pip', commandline,
                                                                  after=os_removedirs_eggs_id,
                                                                  condition=CONDITION_DURING_INSTALL_OR_REPAIR,
                                                                  silent_launcher_file_id=silent_launcher_file_id,
                                                                  text="Running get-pip.py, this may take a few minutes")

        return action.id

    def _append_bootstrap_custom_action(self, wix, os_removedirs_eggs_id, silent_launcher_file_id):
        commandline = r'''"[INSTALLDIR]parts\python\bin\python.exe" -m pythonpy "zc.buildout.buildout.main(list(('-U',)))"'''
        action = wix.add_deferred_in_system_context_custom_action('bootstrap', commandline,
                                                                  after=os_removedirs_eggs_id,
                                                                  condition=CONDITION_DURING_INSTALL_OR_REPAIR,
                                                                  silent_launcher_file_id=silent_launcher_file_id,
                                                                  text="Running buildout bootstrap, this may take a few minutes")

        return action.id

    def _append_delete_extra_executables_custom_action(self, wix, bootstrap_id, silent_launcher_file_id):
        from itertools import product
        after = bootstrap_id
        scripts_to_delete = ["console-script-test", "gui-script-test", "replace_console_script", "script-launcher", "pip*", "easy_install*"]
        suffixes = ['.exe', '-script.py']
        commandline = r'''"[INSTALLDIR]parts\python\bin\python.exe" -c "import glob, os; files = glob.glob(os.path.join('bin', '{}')); list(os.remove(filepath) for filepath in files);"'''

        for index, (prefix, suffix) in enumerate(product(scripts_to_delete, suffixes)):
            commands = ["import glob, os", ]
            after = wix.add_deferred_in_system_context_custom_action('delete_extra_executables_{}'.format(index), commandline.format("{}*{}".format(prefix, suffix)),
                                                                     after=bootstrap_id,
                                                                     condition=CONDITION_DURING_INSTALL_OR_REPAIR,
                                                                     silent_launcher_file_id=silent_launcher_file_id,
                                                                     text="Removing temporary executables, this may take a few minutes")
        return after.id

    def _append_close_application_action(self, wix, silent_launcher_file_id):
        commandline = r'"[INSTALLDIR]bin\buildout.exe" -U install debug-logging close-application'
        action = wix.add_deferred_in_system_context_custom_action('close_application', commandline,
                                                                  after='InstallInitialize',
                                                                  condition=CONDITION_DURING_UPGRADE_AND_UNINSTALL,
                                                                  silent_launcher_file_id=silent_launcher_file_id,
                                                                  text="Closing open applications, this may take a few minutes")
        return action.id

    def _append_pip_uninstall_buildout_stuff(self, wix, close_application_id, silent_launcher_file_id):
        commandline = r'"[INSTALLDIR]parts\python\bin\python.exe" -m pip uninstall zc.buildout buildout.wheel pythonpy --yes --isolated'
        action = wix.add_deferred_in_system_context_custom_action('pip_uninstall', commandline,
                                                                  after=close_application_id,
                                                                  condition=CONDITION_DURING_UPGRADE_AND_UNINSTALL,
                                                                  silent_launcher_file_id=silent_launcher_file_id,
                                                                  text="Removing package temporary files, this may take a few minutes")
        return action.id

    def _append_os_removedirs_eggs_uninstall(self, wix, pip_uninstall_id, silent_launcher_file_id):
        commandline = r'''"[INSTALLDIR]parts\python\bin\python.exe" "-c" "from shutil import rmtree; rmtree('eggs', True)"'''
        action = wix.add_deferred_in_system_context_custom_action('os_removedirs_eggs_uninstall', commandline,
                                                                  after=pip_uninstall_id,
                                                                  condition=CONDITION_DURING_UPGRADE_AND_UNINSTALL,
                                                                  silent_launcher_file_id=silent_launcher_file_id,
                                                                  text="Removing temporary egg files, this may take a few minutes")
        return action.id

    def _append_custom_actions(self, wix, silent_launcher_file_id):
        os_removedirs_eggs_id = self._append_os_removedirs_eggs(wix, silent_launcher_file_id)
        get_pip_id = self._append_get_pip_custom_action(wix, os_removedirs_eggs_id, silent_launcher_file_id)
        bootstrap_id = self._append_bootstrap_custom_action(wix, get_pip_id, silent_launcher_file_id)
        delete_executables_id = self._append_delete_extra_executables_custom_action(wix, bootstrap_id, silent_launcher_file_id)
        close_application_id = self._append_close_application_action(wix, silent_launcher_file_id)
        pip_uninstall_id = self._append_pip_uninstall_buildout_stuff(wix, close_application_id, silent_launcher_file_id)
        os_removedirs_eggs_uninstall_id = self._append_os_removedirs_eggs_uninstall(wix, pip_uninstall_id, silent_launcher_file_id)

    def _add_launch_conditions(self, wix):
        self._add_os_requirements_launch_condition(wix)
        self._prevent_32bit_installations_on_64bit_os(wix)

    def _prevent_32bit_installations_on_64bit_os(self, wix):
        from sys import maxsize
        is_64 = maxsize > 2 ** 32
        if is_64:
            return
        wix.add_condition(OS_32BIT_ON_64BIT_LAUNCH_CONDITION_MESSAGE, "Not VersionNT64")

    def _add_os_requirements_launch_condition(self, wix):
        wix.add_condition(OS_REQUIREMENTS_LAUNCH_CONDITION_MESSAGE, self._calculate_os_requirements())

    def _calculate_os_requirements(self):
        # the launch condition is conjcution of all operating systems that are NOT allowed
        # i.e. if you want to install on X, then the condition of X must not appear in the final condition
        prevent_installation_on_operating_systems = set()
        for name, value in OPERATING_SYSTEMS.items():
            default, condition = value
            if self.get_recipe_section().get("install-on-{}".format(name.lower().replace(' ', '-')), default):
                prevent_installation_on_operating_systems.add(condition)
        return " Or ".join([condition for condition in prevent_installation_on_operating_systems])

    def _add_project_entry_points(self, wix, silent_launcher_file_id):
        for key, value in {'post_install': {'after': 'custom_action_bootstrap',
                                            'before': None,
                                            'condition': CONDITION_DURING_INSTALL_OR_REPAIR},
                           'pre_uninstall': {'after': None,
                                             'before': 'custom_action_close_application',
                                             'condition': CONDITION_DURING_UNINSTALL_NOT_UPGRADE}, }.items():
            script_name = self.get_script_name(key)
            if script_name in ['', 'None', None]:
                continue
            args = self.get_script_args(key)
            commandline = r'"[INSTALLDIR]\bin\{}.exe" {}'.format(script_name, args)
            text = "Running {} actions, this may take a few minutes".format(key.replace('_', ' '))
            wix.add_deferred_in_system_context_custom_action(script_name, commandline,
                                                             after=value['after'], before=value['before'],
                                                             condition=value['condition'],
                                                             silent_launcher_file_id=silent_launcher_file_id,
                                                             text=text)

    def _add_shortcuts(self, wix):
        if not self.get_startmenu_shortcuts() or not self.get_shortcuts_icon():
            return
        icon_id = wix.add_icon(self.get_shortcuts_icon())
        for item in eval(self.get_startmenu_shortcuts()):
            shortcut_name, executable_name = item.split('=')
            wix.add_shortcut(shortcut_name.strip(), executable_name.strip(), icon_id)

    def get_msi_filepath(self):
        return path.join(self.get_working_directory(), "{}-{}-{}.msi".format(self.get_package_name(),
                                                                      self.get_project_version__long(),
                                                                      self.get_os_string()))
