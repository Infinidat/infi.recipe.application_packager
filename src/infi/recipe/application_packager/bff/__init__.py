__import__('pkg_resources').declare_namespace(__name__)

import re
import os
import shutil
import logging

from ..base import PackagingRecipe, RECIPE_DEFAULTS
from .. import utils

logger = logging.getLogger(__name__)

TEMPLATE = 'template'
POSTINSTALL = 'postinstall'
PREREMOVE = 'preremove'


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
            package = self.build_package()
            logger.info('Built {}'.format(package))
            return [package]

    def build_package(self):
        self._files = set()
        with utils.temporary_directory_context() as buildroot:
            self.buildroot = buildroot
            self.put_all_files()
            with utils.temporary_directory_context() as temproot:
                self.temproot = temproot
                self._create_template(POSTINSTALL, mode=0o755)
                self._create_template(PREREMOVE, mode=0o755)
                self._create_template(TEMPLATE)
                self._bffbuild()
            if os.path.exists(self.bff_filepath):
                os.remove(self.bff_filepath)
            shutil.copy(os.path.join('tmp', self.bff_filename), self.bff_filepath)
            return self.bff_filepath

    def _bffbuild(self):
        cmd = ['mkinstallp', '-T', TEMPLATE, '-d', self.buildroot]
        return utils.execute.execute_assert_success(cmd).get_stdout().decode()

    def _create_template(self, name, mode=0o644):
        from jinja2 import Environment, PackageLoader
        loader = PackageLoader(__name__, 'templates')
        environment = Environment(loader=loader)
        template = environment.get_template(name + '.in')
        kwargs = self.get_template_kwargs()
        content = template.render(kwargs)
        flags = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
        fd = os.open(name, flags, mode=mode)
        os.write(fd, content.encode())
        os.close(fd)

    def _mkdir(self, name, parent_directory, just_add_it=False):
        dst = os.path.join(parent_directory, name)
        src = "{}{}/{}".format(self.buildroot, parent_directory, name)
        os.makedirs(src) if not just_add_it else None
        return dst

    def _add_directory(self, src, parent_directory, recursive=True, only_directory_tree=False):
        source_dirname = os.path.basename(src)
        destination_directory = self._mkdir(source_dirname, parent_directory, only_directory_tree)
        for filename in os.listdir(src):
            filepath = os.path.join(src, filename)
            if os.path.isfile(filepath):
                if filename.endswith('pyc') or only_directory_tree:
                    continue
                self._add_file(filepath, destination_directory)
            elif recursive:
                self._add_directory(filepath, destination_directory, recursive, only_directory_tree)

    def _add_file(self, source_filepath, destination_directory, destination_filename=None):
        if os.path.dirname(source_filepath) == '':
            source_filepath = os.path.join(self.get_buildout_dir(), source_filepath)
        if destination_filename is None:
            destination_filename = os.path.basename(source_filepath)
        buildroot_filepath = "{}{}/{}".format(self.buildroot, destination_directory, destination_filename)
        destination_filepath = os.path.join(destination_directory, destination_filename)
        if destination_directory == os.path.join(self.get_install_prefix(), 'parts', 'python', 'bin'):
            if 'python' not in destination_filename:
                logger.debug('Skip script file %s', destination_filepath)
                return
        if 'site-packages' in destination_directory:
            logger.debug('Skip site-packages file %s', destination_filepath)
            return
        if destination_directory.endswith('egg-info'):
            logger.debug('Skip egg-info files %s', destination_filepath)
            return
        if re.search(r'[\s{}()]+', destination_filepath):
            logger.warning('HPT-3161: skip %s file', destination_filepath)
            return
        self.copy_file(source_filepath, buildroot_filepath)
        self._files.add(destination_directory)
        self._files.add(destination_filepath)

    def get_template_kwargs(self):
        scripts = []
        console_scripts = self.get_console_scripts_for_production()
        gui_scripts = self.get_gui_scripts_for_production()
        post_install = self.get_script_name('post_install')
        pre_uninstall = self.get_script_name('pre_uninstall')
        if console_scripts:
            scripts += console_scripts.split()
        if gui_scripts:
            scripts += gui_scripts.split()
        if post_install in scripts:
            scripts.remove(post_install)
        if pre_uninstall in scripts:
            scripts.remove(pre_uninstall)
        kwargs = {
            'temproot': self.temproot,
            'product': self.get_product_name(),
            'description': self.get_description(),
            'package': self.get_package_name(),
            'version': self.get_package_vrmf(),
            'prefix': self.get_install_prefix(),
            'post_install': post_install,
            'pre_uninstall': pre_uninstall,
            'files': sorted(self._files),
            'scripts': sorted(scripts)
        }
        return kwargs

    def put_all_files(self):
        os.makedirs('{}{}'.format(self.buildroot, self.get_install_prefix()))
        self._mkdir(self.get_install_prefix(), os.path.sep, True)
        self._add_file('get-pip.py', self.get_install_prefix())
        self._add_file('buildout.in', self.get_install_prefix(), 'buildout.cfg')
        self._add_file('setup.py', self.get_install_prefix())
        cachedir = self._mkdir('.cache', self.get_install_prefix())
        develop_eggs = self._mkdir('develop-eggs', self.get_install_prefix())
        self._add_directory(os.path.join(self.get_buildout_dir(), '.cache', 'dist'), cachedir, recursive=False)
        parts = self._mkdir('parts', self.get_install_prefix())
        self._mkdir('bin', self.get_install_prefix())
        self._mkdir('buildout', parts)
        self._mkdir('production-scripts', parts)
        self._add_directory(os.path.join(self.get_buildout_dir(), 'parts', 'python'), parts)
        self._add_directory(os.path.join(self.get_buildout_dir(), 'src'), self.get_install_prefix())
        self._add_directory(os.path.join(self.get_buildout_dir(), 'eggs'), self.get_install_prefix(), True, True)
        self.add_aditional_directories()

    # HOSTDEV-3578: BFF version should be: Version.Release.Modification.FixLevel
    def get_package_vrmf(self):
        from infi.os_info.parse_version import parse_version
        version = self.get_project_version__short()
        octets = list()
        for octet in parse_version(version):
            if not octet.isdigit():
                break
            octets.append(int(octet))
        while len(octets) < 4:
            octets.append(0)
        while len(octets) > 4:
            octets.pop()
        return '.'.join([str(octet) for octet in octets])

    @property
    def bff_filename(self):
        name = self.get_package_name()
        vrmf = self.get_package_vrmf()
        return '%s.%s.bff' % (name, vrmf)

    @property
    def bff_filepath(self):
        directory = self.get_working_directory()
        name = self.get_package_name()
        version = self.get_project_version__long()
        info = self.get_os_string()
        filename = '%s-%s-%s.bff' % (name, version, info)
        return os.path.join(directory, filename)
