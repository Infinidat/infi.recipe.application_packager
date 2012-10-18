__import__("pkg_resources").declare_namespace(__name__)

from logging import getLogger
from ..base import PackagingRecipe, RECIPE_DEFAULTS
from .. import utils, assertions
from os import path, curdir, makedirs, listdir
from shutil import rmtree, copy
from pkg_resources import resource_filename
from contextlib import contextmanager

logger = getLogger(__name__)

BYPASS_CUSTOM_ACTION_PROPERTY = "NO_CUSTOM_ACTIONS"
CONDITION_DURING_INSTALL_OR_REPAIR = 'NOT Installed OR MaintenanceMode="Modify"'
CONDITION_DURING_UNINSTALL_NOT_UPGRADE = 'REMOVE="ALL" AND NOT UPGRADINGPRODUCTCODE'
DowngradeErrorMessage = 'A later version of [ProductName] is already installed. Setup will now exit.'
LAUNCH_CONDITION__WINDOWS_2008_AND_R2_ONLY = \
    "(Not Version9X) And (Not VersionNT=400) And (Not VersionNT=500) And (Not VersionNT=501) And" + \
    "(Not VersionNT=502) And (Not (VersionNT=600 And (MsiNTProductType=1))) And " + \
    "(Not (VersionNT=601 And (MsiNTProductType=1)))"
OS_REQUIREMENTS_LAUNCH_CONDITION_MESSAGE = "The operating system is not adequate for running [ProductName]."
OS_32BIT_ON_64BIT_LAUNCH_CONDITION_MESSAGE = "[ProductName] installation on a 64-bit operating system requires the 64-bit installation package. Please get the 64-bit package and try again."
OPERATING_SYSTEMS = {
                     # OS Name: (allow-install, condition)
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
        self.signtool = self.get_signtool()
        self.write_buildout_configuration_file_for_production()
        utils.download_buildout(self.get_download_cache_dist())
        utils.download_distribute(self.get_download_cache_dist())
        silent_launcher = self.get_silent_launcher()
        if self.should_sign_files():
            self.sign_all_executables_in_project()
            self.signtool.sign_file(silent_launcher)
        package = self.build_package(silent_launcher)
        logger.debug("Built {}".format(package))
        if self.should_sign_files():
            self.signtool.sign_file(package)
            logger.debug("Signed {}".format(package))
        return [package, ]

    def get_silent_launcher(self):
        from tempfile import mkstemp
        from shutil import copy
        from os import close
        fd, abspath = mkstemp()
        close(fd)
        launcher = resource_filename(__name__, SILENT_LAUNCHER.format(self.get_platform_arch()))
        copy(launcher, abspath)
        return abspath

    def get_signtool(self):
        recipe = self.get_recipe_section()
        timestamp_url = recipe.get("timestamp-url", RECIPE_DEFAULTS['timestamp-url'])
        certificate = recipe.get("pfx-file", RECIPE_DEFAULTS['pfx-file'])
        password_file = recipe.get("pfx-password-file", RECIPE_DEFAULTS['pfx-password-file'])
        return utils.signtool.Signtool(timestamp_url, certificate, password_file)

    def sign_all_executables_in_project(self):
        for archive_path in self.glob_in_dist_directory("distribute*"):
            self.signtool.sign_executables_in_archive(archive_path)
        for archive_path in self.glob_in_dist_directory("infi.recipe.console_scripts*"):
            self.signtool.sign_executables_in_archive(archive_path)
        # The original python executable is running, cannot sign it
        # self.signtool.sign_file(path.join(self.get_buildout_dir(), 'parts', 'python', 'bin', 'python.exe'))

    def glob_in_dist_directory(self, basename):
        from glob import glob
        return glob(path.join(self.get_download_cache_dist(), "dist", basename))

    def write_wix_to_destionation_directory(self, wix):
        import lxml.etree
        src = path.join(self.get_working_directory(), 'product.wxs')
        with open(src, 'w') as fd:
            xml = lxml.etree.tostring(wix._content)
            fd.write(xml)
        return src

    def build_package(self, silent_launcher):
        wix = self.prepare_wix(silent_launcher)
        wix_filepath = self.write_wix_to_destionation_directory(wix)
        with self.wix_context() as wix_basedir:
            wix.build(wix_basedir, wix_filepath, self.get_msi_filepath())
        return self.get_msi_filepath()

    def prepare_wix(self, silent_launcher):
        from .wix import Wix
        wix = Wix(self.get_product_name(), self.get_project_version__short(),
                  self.get_platform_arch(), self.get_upgrade_code(), self.get_description(),
                  self.get_company_name())
        silent_launcher_file_id = self._put_all_files(wix, silent_launcher)
        self._append_bindir_to_system_path(wix)
        self._append_custom_actions(wix, silent_launcher_file_id)
        self._prepare_for_major_upgrade(wix)
        self._add_launch_conditions(wix)
        self._add_project_entry_points(wix, silent_launcher_file_id)
        arp_icon = self.get_add_remove_programs_icon()
        if arp_icon:
            arp_icon = wix.set_add_remove_programs_icon(arp_icon)
        self._add_shortcuts(wix)
        banner_bmp = self.get_msi_banner_bmp()
        if banner_bmp:
            logger.info("Setting custom banner {}".format(banner_bmp))
            wix.new_element("WixVariable", {"Id": "WixUIBannerBmp", "Value": banner_bmp}, wix.product)
        dialog_bmp = self.get_msi_dialog_bmp()
        if dialog_bmp:
            logger.info("Setting custom dialog {}".format(dialog_bmp))
            wix.new_element("WixVariable", {"Id": "WixUIDialogBmp", "Value": dialog_bmp}, wix.product)
        return wix

    @contextmanager
    def wix_context(self):
        from archive import extract
        with utils.temporary_directory_context() as tempdir:
            wix_archive = self.get_wix35_binaries_zip_from_the_internet()
            extract(wix_archive)
            yield tempdir

    def get_wix35_binaries_zip_from_the_internet(self):
        from urllib import urlretrieve
        from tempfile import mkstemp
        from os import close
        fd, path = mkstemp(suffix='.zip')
        close(fd)
        urlretrieve("ftp://python.infinidat.com/archives/wix-binaries-v3.5-windows-x86.zip", path)
        return path

    def _append_bindir_to_system_path(self, wix):
        from .wix import generate_guid
        bindir = wix.mkdir('bin', wix.installdir)
        assembly_dir = wix.mkdir('Microsoft.VC90.CRT', bindir)
        component = wix.new_component(wix.new_id('bin'), bindir, generate_guid())
        wix.add_environment_variable('Path', r'[INSTALLDIR]bin', component)
        wix.add_delete_all_files_on_removal_component_to_directory(bindir)
        wix.add_delete_empty_folder_component_to_directory(bindir)

    def _put_all_files(self, wix, silent_launcher):
        wix.add_file('bootstrap.py', wix.installdir)
        wix.add_file('buildout.in', wix.installdir, 'buildout.cfg')
        wix.add_file('setup.py', wix.installdir)
        cachedir = wix.mkdir('.cache', wix.installdir)
        silent_launcher_file_id = wix.add_file(silent_launcher, cachedir).get('Id')
        develop_eggs = wix.mkdir('develop-eggs', wix.installdir)
        wix.add_directory(self.get_download_cache_dist(), cachedir)
        parts = wix.mkdir('parts', wix.installdir)
        wix.mkdir('buildout', parts)
        wix.mkdir('production-scripts', parts)
        wix.add_directory(path.join(self.get_buildout_dir(), 'parts', 'python'), parts)
        wix.add_directory(path.join(self.get_buildout_dir(), 'src'), wix.installdir)
        wix.add_directory(path.join(self.get_buildout_dir(), 'eggs'), wix.installdir, True, True)
        wix.add_delete_all_files_on_removal_component_to_directory(wix.installdir)
        wix.add_delete_empty_folder_component_to_directory(wix.installdir)
        return silent_launcher_file_id

    def _append_os_removedirs_eggs(self, wix, silent_launcher_file_id):
        commandline = r'''"[INSTALLDIR]parts\python\bin\python.exe" "-c" "from shutil import rmtree; rmtree('[INSTALLDIR]eggs', True)"'''
        action = wix.add_deferred_in_system_context_custom_action('os_removedirs_eggs', commandline,
                                                                  condition=CONDITION_DURING_INSTALL_OR_REPAIR,
                                                                  silent_launcher_file_id=silent_launcher_file_id)
        return action.get('Id')

    def _append_bootstrap_custom_action(self, wix, os_removedirs_eggs_id, silent_launcher_file_id):
        commandline = r'"[INSTALLDIR]parts\python\bin\python.exe" bootstrap.py ' + \
                      r'--download-base=.cache\dist --setup-source=.cache\dist\distribute_setup.py'
        action = wix.add_deferred_in_system_context_custom_action('bootstrap', commandline,
                                                                  after=os_removedirs_eggs_id,
                                                                  condition=CONDITION_DURING_INSTALL_OR_REPAIR,
                                                                  silent_launcher_file_id=silent_launcher_file_id)
        return action.get('Id')

    def _append_buildout_custom_action(self, wix, bootstrap_id, silent_launcher_file_id):
        action = wix.add_deferred_in_system_context_custom_action('buildout', r'"[INSTALLDIR]bin\buildout.exe"',
                                                                  after=bootstrap_id,
                                                                  condition=CONDITION_DURING_INSTALL_OR_REPAIR,
                                                                  silent_launcher_file_id=silent_launcher_file_id)

    def _append_custom_actions(self, wix, silent_launcher_file_id):
        os_removedirs_eggs_id = self._append_os_removedirs_eggs(wix, silent_launcher_file_id)
        bootstrap_id = self._append_bootstrap_custom_action(wix, os_removedirs_eggs_id, silent_launcher_file_id)
        self._append_buildout_custom_action(wix, bootstrap_id, silent_launcher_file_id)
        wix.new_element("Property", {"Id": BYPASS_CUSTOM_ACTION_PROPERTY, "Value":"0"}, wix.product)

    def _add_launch_conditions(self, wix):
        self._add_os_requirements_launch_condition(wix)
        self._prevent_32bit_installations_on_64bit_os(wix)

    def _prevent_32bit_installations_on_64bit_os(self, wix):
        from sys import maxsize
        is_64 = maxsize > 2 ** 32
        if is_64:
            return
        condition = wix.new_element("Condition", {'Message': OS_32BIT_ON_64BIT_LAUNCH_CONDITION_MESSAGE},
                                    wix.product)
        condition.text = "Not VersionNT64"

    def _add_os_requirements_launch_condition(self, wix):
        condition = wix.new_element("Condition", {'Message': OS_REQUIREMENTS_LAUNCH_CONDITION_MESSAGE},
                                    wix.product)
        condition.text = self._calculate_os_requirements() + (wix.product.text or '')

    def _calculate_os_requirements(self):
        # the launch condition is conjcution of all operating systems that are NOT allowed
        # i.e. if you want to install on X, then the condition of X must not appear in the final condition
        prevent_installation_on_operating_systems = set()
        for name, value in OPERATING_SYSTEMS.items():
            default, condition = value
            if self.get_recipe_section().get("install-on-{}".format(name.lower().replace(' ', '-')), default):
                prevent_installation_on_operating_systems.add(condition)
        return " Or ".join([condition for condition in prevent_installation_on_operating_systems])

    def _prepare_for_major_upgrade(self, wix):
        wix.new_element("MajorUpgrade", {'AllowDowngrades': 'no',
                                          'AllowSameVersionUpgrades': 'yes',
                                          'DowngradeErrorMessage': DowngradeErrorMessage,
                                          'IgnoreRemoveFailure': 'yes',
                                          }, wix.product)

    def _add_project_entry_points(self, wix, silent_launcher_file_id):
        for key, value in {'post_install': {'after': 'custom_action_buildout',
                                            'condition': CONDITION_DURING_INSTALL_OR_REPAIR},
                           'pre_uninstall': {'after': 'InstallInitialize',
                                             'condition': CONDITION_DURING_UNINSTALL_NOT_UPGRADE}, }.items():
            script_name = self.get_script_name(key)
            if script_name in ['', None]:
                continue
            args = self.get_script_args(key)
            commandline = r'"[INSTALLDIR]\bin\{}.exe" {}'.format(script_name, args)
            wix.add_deferred_in_system_context_custom_action(script_name, commandline, after=value['after'],
                                                             condition=value['condition'],
                                                             silent_launcher_file_id=silent_launcher_file_id)

    def _add_shortcuts(self, wix):
        if not self.get_startmenu_shortcuts() or not self.get_shortcuts_icon():
            return
        icon_id = wix.new_icon(self.get_shortcuts_icon())
        for item in eval(self.get_startmenu_shortcuts()):
            shortcut_name, executable_name = item.split('=')
            wix.add_shortcut(shortcut_name.strip(), executable_name.strip(), icon_id)

    def get_msi_filepath(self):
        return path.join(self.get_working_directory(), "{}-{}-{}.msi".format(self.get_package_name(),
                                                                      self.get_project_version__long(),
                                                                      self.get_os_string()))



