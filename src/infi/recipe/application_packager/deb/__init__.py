__import__('pkg_resources').declare_namespace(__name__)

import logging
import os
from infi.recipe.application_packager.base import PackagingRecipe, RECIPE_DEFAULTS
from infi.recipe.application_packager import utils

logger = logging.getLogger(__name__)

DEBIAN = 'DEBIAN'
CONTROL = 'control'
CHANGELOG = 'changelog'
RULES = 'rules'
PREINST = 'preinst'
POSTINST = 'postinst'
PRERM = 'prerm'
POSTRM = 'postrm'

TEMPLATES = {
    CONTROL: 0o644,
    CHANGELOG: 0o644,
    RULES: 0o755,
    PREINST: 0o755,
    POSTINST: 0o755,
    PRERM: 0o755,
    POSTRM: 0o755
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
            logger.debug('Built %s', self.deb_path)
            return [self.deb_path]

    def build(self):
        with utils.temporary_directory_context() as buildroot:
            self.buildroot = buildroot
            self.copy_tree()
            self.walk_tree()
            self.create_deb_files()
            self.build_deb_package()

    def build_deb_package(self):
        cmd = ['fakeroot', '--', 'dpkg-deb', '-b', self.buildroot, self.deb_path]
        utils.execute.execute_assert_success(cmd)

    def get_dependencies(self):
        dependencies = self.get_recipe_section().get('deb-dependencies', RECIPE_DEFAULTS['deb-dependencies'])
        dependencies = [dependency.strip() for dependency in dependencies.splitlines()]
        return 'Depends: {}'.format(', '.join(dependencies)) if dependencies else ''

    def get_deb_kwargs(self):
        return {
            'prefix': self.get_install_prefix(),
            'package': self.get_package_name(),
            'version': self.get_project_version__short(),
            'arch': self.get_target_arch(),
            'summary': self.get_product_name(),
            'description': self.get_description(),
            'company': self.get_company_name(),
            'dependencies': self.get_dependencies(),
            'post_install_script_name': self.get_script_name('post_install') or '',
            'post_install_script_args': self.get_script_args('post_install') or '',
            'pre_uninstall_script_name': self.get_script_name("pre_uninstall") or '',
            'pre_uninstall_script_args': self.get_script_args('pre_uninstall') or '',
            'close' : '1' if self.should_close_app_on_upgrade_or_removal() else '0',
            'scripts': self.get_scripts(),
            'url': self.get_url()
        }

    def create_deb_files(self):
        kwargs = self.get_deb_kwargs()
        os.makedirs(DEBIAN)
        with utils.chdir(DEBIAN):
            for name, mode in TEMPLATES.items():
                self.render_template(__name__, name, kwargs, mode)

    @property
    def deb_name(self):
        name = self.get_package_name()
        version = self.get_project_version__long()
        info = self.get_os_string()
        return "{}-{}-{}.deb".format(name, version, info)

    @property
    def deb_path(self):
        return os.path.join(self.get_working_directory(), self.deb_name)
