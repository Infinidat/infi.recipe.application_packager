__import__('pkg_resources').declare_namespace(__name__)

import logging
import re
import os
import shutil

from infi.recipe.application_packager.base import PackagingRecipe, RECIPE_DEFAULTS
from infi.recipe.application_packager import utils

logger = logging.getLogger(__name__)

SPEC = 'rpm.spec'

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
            logger.debug('Built %s', self.rpm_path)
            return [self.rpm_path]

    def build(self):
        with utils.temporary_directory_context() as buildroot:
            self.buildroot = buildroot
            self.copy_tree()
            self.walk_tree()
            with utils.temporary_directory_context():
                self.create_rpm_files()
                package = self.build_rpm_package()
                if os.path.exists(self.rpm_path):
                    os.remove(self.rpm_path)
                shutil.copy(package, self.rpm_path)

    def build_rpm_package(self):
        cmd = ['rpmbuild', '--verbose', '--noclean', '--buildroot',
               self.buildroot, '-bb', SPEC]
        process = utils.execute.execute_assert_success(cmd)
        output = process.get_stdout().decode()
        package = re.search('Wrote: (.*)', output).groups()[0]
        return package

    def create_rpm_files(self):
        kwargs = self.get_rpm_kwargs()
        self.render_template(__name__, SPEC, kwargs)

    def get_dependencies(self):
        dependencies = self.get_recipe_section().get('rpm-dependencies', RECIPE_DEFAULTS['rpm-dependencies'])
        dependencies = [dependency.strip() for dependency in dependencies.splitlines()]
        return '\n'.join(['Requires: {}'.format(dependency) for dependency in dependencies])

    def get_rpm_kwargs(self):
        return {
           'buildroot': self.buildroot,
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
           'pre_uninstall_script_name': self.get_script_name('pre_uninstall') or '',
           'pre_uninstall_script_args': self.get_script_args('pre_uninstall') or '',
           'directories': sorted(self.directories),
           'files': sorted(self.files),
           'close' : '1' if self.should_close_app_on_upgrade_or_removal() else '0',
           'scripts': self.get_scripts(),
           'url': self.get_url()
        }

    @property
    def rpm_name(self):
        name = self.get_package_name()
        version = self.get_project_version__long()
        info = self.get_os_string()
        return '{}-{}-{}.rpm'.format(name, version, info)

    @property
    def rpm_path(self):
        return os.path.join(self.get_working_directory(), self.rpm_name)
