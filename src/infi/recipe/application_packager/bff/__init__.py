__import__('pkg_resources').declare_namespace(__name__)

import logging
import os
import shutil
from infi.os_info.parse_version import parse_version
from infi.recipe.application_packager.base import PackagingRecipe, RECIPE_DEFAULTS
from infi.recipe.application_packager import utils

logger = logging.getLogger(__name__)

TMP = 'tmp'
SPEC = 'bff.spec'
PREINSTALL = 'preinstall'
POSTINSTALL = 'postinstall'
PREREMOVE = 'preremove'
POSTREMOVE = 'postremove'

TEMPLATES = {
    SPEC: 0o644,
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
            logger.info('Built %s', self.bff_path)
            return [self.bff_path]

    def build(self):
        with utils.temporary_directory_context() as buildroot:
            self.buildroot = buildroot
            self.copy_tree()
            self.walk_tree()
            with utils.temporary_directory_context() as temproot:
                self.temproot = temproot
                self.write_bff_files()
                package = self.build_bff_package()
            if os.path.exists(self.bff_path):
                os.remove(self.bff_path)
            shutil.copy(package, self.bff_path)

    def build_bff_package(self):
        cmd = ['mkinstallp', '-T', SPEC, '-d', self.buildroot]
        utils.execute.execute_assert_success(cmd)
        return os.path.join(TMP, self.bff_name)

    def get_bff_kwargs(self):
        return {
            'temproot': self.temproot,
            'prefix': self.get_install_prefix(),
            'package': self.get_package_name(),
            'version': self.get_package_vrmf(),
            'arch': self.get_target_arch(),
            'summary': self.get_product_name(),
            'description': self.get_description(),
            'post_install_script_name': self.get_script_name('post_install') or '',
            'post_install_script_args': self.get_script_args('post_install') or '',
            'pre_uninstall_script_name': self.get_script_name('pre_uninstall') or '',
            'pre_uninstall_script_args': self.get_script_args('pre_uninstall') or '',
            'files': sorted(self.files),
            'directories': sorted(self.directories),
            'close' : '1' if self.should_close_app_on_upgrade_or_removal() else '0',
            'scripts': self.get_scripts()
        }

    def write_bff_files(self):
        kwargs = self.get_bff_kwargs()
        for name, mode in TEMPLATES.items():
            self.render_template(__name__, name, kwargs, mode)

    # HOSTDEV-3578: BFF version should be: Version.Release.Modification.FixLevel
    def get_package_vrmf(self):
        version = self.get_project_version__short()
        octets = []
        for octet in parse_version(version):
            if not octet.isdigit():
                break
            octets.append(int(octet))
        while len(octets) < 4:
            octets.append(0)
        if not len(octets) == 4:
            raise NotImplementedError('version number %s contains more than 4 octets and not supported by AIX BFF package manager' % version)
        return '.'.join([str(octet) for octet in octets])

    @property
    def bff_name(self):
        name = self.get_package_name()
        vrmf = self.get_package_vrmf()
        return '%s.%s.bff' % (name, vrmf)

    @property
    def bff_path(self):
        directory = self.get_working_directory()
        name = self.get_package_name()
        vrmf = self.get_package_vrmf()
        info = self.get_os_string()
        filename = '%s-%s-%s.bff' % (name, vrmf, info)
        return os.path.join(directory, filename)
