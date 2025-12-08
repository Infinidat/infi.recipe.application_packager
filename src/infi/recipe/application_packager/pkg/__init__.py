__import__('pkg_resources').declare_namespace(__name__)

import datetime
import logging
import os
import platform
import shutil
from infi.recipe.application_packager.base import PackagingRecipe, RECIPE_DEFAULTS
from infi.recipe.application_packager import utils

logger = logging.getLogger(__name__)

SPACE = 'space'
PROTOTYPE = 'prototype'
PKGINFO = 'pkginfo'
CHECKINSTALL = 'checkinstall'
PREINSTALL = 'preinstall'
PREREMOVE = 'preremove'
POSTINSTALL = 'postinstall'
POSTREMOVE = 'postremove'

TEMPLATES = {
    SPACE: 0o644,
    PROTOTYPE: 0o644,
    PKGINFO: 0o644,
    CHECKINSTALL: 0o755,
    PREINSTALL: 0o755,
    POSTINSTALL: 0o755,
    PREREMOVE: 0o755,
    POSTREMOVE: 0o755
}

class Recipe(PackagingRecipe):
    def install(self):
        with self.with_most_mortem():
            self.delete_non_production_packages_from_cache_dist()
            self.write_get_pip_for_production()
            self.write_buildout_configuration_file_for_production()
            self.download_python_packages_used_by_packaging()
            utils.compiler.compile_binary_distributions(self.get_buildout_dir(),
                                                        self.get_download_cache_dist(),
                                                        self.get_eggs_directory())
            self.convert_python_packages_used_by_packaging_to_wheels()
            self.build()
            logger.debug('Built %s', self.pkg_path)
            return [self.pkg_path]

    def build(self):
        with utils.temporary_directory_context() as buildroot:
            self.buildroot = buildroot
            self.copy_tree()
            self.walk_tree()
            with utils.temporary_directory_context() as temproot:
                self.temproot = temproot
                self.write_pkg_files()
                package = self.build_pkg_package()
                if os.path.exists(self.pkg_path):
                    os.remove(self.pkg_path)
                shutil.copy(package, self.pkg_path)

    def build_pkg_proto(self):
        prefix = self.get_install_prefix()
        opt = '.{}={}'.format(prefix, prefix)
        cmd = ['pkgproto', opt]
        with utils.chdir(self.buildroot):
            process = utils.execute.execute_assert_success(cmd)
        return process.get_stdout().decode()

    def build_pkg_package(self):
        cmd = ['pkgmk', '-o', '-r', self.buildroot, '-d', self.temproot, '-f', PROTOTYPE]
        utils.execute.execute_assert_success(cmd)
        cmd = ['pkgtrans', '-s', self.temproot, self.pkg_name, self.get_package_name()]
        utils.execute.execute_assert_success(cmd)
        cmd = ['gzip', '-9', '-v', self.pkg_name]
        utils.execute.execute_assert_success(cmd)
        return '{}.gz'.format(self.pkg_name)

    def get_pkg_kwargs(self):
        return {
            'prefix': self.get_install_prefix(),
            'package': self.get_package_name(),
            'version': self.get_project_version__short(),
            'revision': self.get_package_revision(),
            'arch': self.get_target_arch(),
            'isa': self.get_target_isa(),
            'summary': self.get_product_name(),
            'description': self.get_description(),
            'company': self.get_company_name(),
            'post_install_script_name': self.get_script_name('post_install') or '',
            'post_install_script_args': self.get_script_args('post_install') or '',
            'pre_uninstall_script_name': self.get_script_name('pre_uninstall') or '',
            'pre_uninstall_script_args': self.get_script_args('pre_uninstall') or '',
            'proto': self.build_pkg_proto(),
            'close' : '1' if self.should_close_app_on_upgrade_or_removal() else '0',
            'scripts': self.get_scripts(),
            'inodes': 2 * self.inodes,
            'blocks': 2 * int(self.bytes / 512)
        }

    def write_pkg_files(self):
        kwargs = self.get_pkg_kwargs()
        for name, mode in TEMPLATES.items():
            self.render_template(__name__, name, kwargs, mode)

    def get_package_revision(self):
        now = datetime.datetime.now()
        return now.strftime('%Y.%m.%d')

    def get_platform_isa(self):
        cmd = ['isainfo', '-n']
        process = utils.execute.execute_assert_success(cmd)
        return process.get_stdout().decode().strip()

    def get_target_isa(self):
        return self._get_recipe_atribute('_target_isa') or self.get_platform_isa()

    @property
    def pkg_name(self):
        name = self.get_package_name()
        version = self.get_project_version__long()
        info = self.get_os_string()
        return '{}-{}-{}.pkg'.format(name, version, info)

    @property
    def pkg_gz_name(self):
        return '{}.gz'.format(self.pkg_name)

    @property
    def pkg_path(self):
        return os.path.join(self.get_working_directory(), self.pkg_gz_name)
