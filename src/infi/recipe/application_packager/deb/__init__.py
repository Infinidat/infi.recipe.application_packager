__import__("pkg_resources").declare_namespace(__name__)

from logging import getLogger
from ..base import PackagingRecipe, RECIPE_DEFAULTS
from .. import utils
from os import path, curdir, makedirs, listdir
from shutil import rmtree, copy
from pkg_resources import resource_filename

logger = getLogger(__name__)

class Recipe(PackagingRecipe):
    def install(self):
        with self.with_most_mortem():
            self.delete_non_production_packages_from_cache_dist()
            self.write_get_pip_for_production()
            self.write_buildout_configuration_file_for_production()
            self.download_python_packages_used_by_packaging()
            utils.compiler.compile_binary_distributions(self.get_buildout_dir(),
                                                        self.get_download_cache_dist(),
                                                        self.get_eggs_directory(),
                                                        self.using_wheels())
            self.convert_python_packages_used_by_packaging_to_wheels()
            package = self.build_package()
            logger.debug("Built {}".format(package))
            return [package, ]

    def build_package(self):
        self._directories = set()
        with utils.temporary_directory_context() as tempdir:
            self._put_all_files()
            self._write_debian_directory()
            self._call_dpkg()
            return self.get_deb_filepath()

    def _mkdir(self, name, parent_directory, just_add_it=False):
        dst = path.join(parent_directory, name)
        src = "{}{}/{}".format(path.abspath(curdir), parent_directory, name)
        makedirs(src) if not just_add_it else None
        self._directories.add(dst)
        return dst

    def _add_directory(self, src, parent_directory, recursive=True, only_directory_tree=False):
        source_dirname = path.basename(src)
        destination_directory = self._mkdir(source_dirname, parent_directory, only_directory_tree)
        for filename in listdir(src):
            filepath = path.join(src, filename)
            if path.isfile(filepath):
                if filename.endswith('pyc') or only_directory_tree:
                    continue
                self._add_file(filepath, destination_directory)
            elif recursive:
                self._add_directory(filepath, destination_directory, recursive, only_directory_tree)

    def _add_file(self, source_filepath, destination_directory, destination_filename=None):
        if path.dirname(source_filepath) == '':
            source_filepath = path.join(self.get_buildout_dir(), source_filepath)
        if destination_filename is None:
            destination_filename = path.basename(source_filepath)
        buildroot_filepath = "{}{}/{}".format(path.abspath(curdir), destination_directory, destination_filename)
        destination_filepath = path.join(destination_directory, destination_filename)
        copy(source_filepath, buildroot_filepath)

    def _put_all_files(self):
        makedirs("{}{}".format(path.abspath(curdir), self.get_install_prefix()))
        self._mkdir(self.get_install_prefix(), path.sep, True)
        self._add_file('get-pip.py', self.get_install_prefix())
        self._add_file('buildout.in', self.get_install_prefix(), 'buildout.cfg')
        self._add_file('setup.py', self.get_install_prefix())
        cachedir = self._mkdir('.cache', self.get_install_prefix())
        develop_eggs = self._mkdir('develop-eggs', self.get_install_prefix())
        self._add_directory(path.join(self.get_buildout_dir(), '.cache', 'dist'), cachedir, recursive=False)
        parts = self._mkdir('parts', self.get_install_prefix())
        self._mkdir('bin', self.get_install_prefix())
        self._mkdir('buildout', parts)
        self._mkdir('production-scripts', parts)
        self._add_directory(path.join(self.get_buildout_dir(), 'parts', 'python'), parts)
        self._add_directory(path.join(self.get_buildout_dir(), 'src'), self.get_install_prefix())
        self._add_directory(path.join(self.get_buildout_dir(), 'eggs'), self.get_install_prefix(), True, True)
        self.add_aditional_directories()

    def get_deb_filename(self):
        return "{}-{}-{}.deb".format(self.get_package_name(), self.get_project_version__long(), self.get_os_string())

    def get_deb_filepath(self):
        return path.join(self.get_working_directory(), self.get_deb_filename())

    def _call_dpkg(self):
        return utils.execute.execute_assert_success(['fakeroot', '--unknown-is-real', '--', 'dpkg-deb',
                                                     '-b', path.abspath(curdir), self.get_deb_filepath()])

    def _clean_debian_directory(self):
        if path.exists("DEBIAN"):
            rmtree("DEBIAN", ignore_errors=True)
        makedirs("DEBIAN")

    def _write_template_file(self, filename, formatting_dict, permissions='644'):
        from string import Template
        src = resource_filename(__name__, filename)
        dst = path.join(curdir, 'DEBIAN', filename.replace('.in', ''))
        with open(src, 'r') as fd:
            template = Template(fd.read())
        with open(dst, 'w') as fd:
            contents = template.substitute(formatting_dict)
            fd.write(contents)
            logger.debug("writing {!r}:\n {}".format(filename, contents))
            utils.execute.execute_assert_success("chmod {} {}".format(permissions, dst).split())

    def _get_depends_declaration(self):
        deb_dependencies = self.get_recipe_section().get("deb-dependencies", RECIPE_DEFAULTS["deb-dependencies"])
        deps= [item.strip() for item in deb_dependencies.splitlines()]
        return "Depends: {}".format(', '.join(deps)) if deps else ''

    def _write_templates(self):
        self._write_template_file('control.in', {'package_name': self.get_package_name(),
                                                 'package_version': self.get_project_version__short(),
                                                 'package_arch': self.get_platform_arch(),
                                                 'company': self.get_company_name(),
                                                 'product_description': self.get_description(),
                                                 'depends_declaration': self._get_depends_declaration(),
                                                 })
        self._write_template_file('changelog.in', {'package_name': self.get_package_name(),
                                                   'package_version': self.get_project_version__short(),
                                                   })
        self._write_template_file('md5sums.in', {})
        post_install_script_name = self.get_script_name("post_install") or ''
        post_install_script_args = self.get_script_args("post_install") or ''
        pre_uninstall_script_name = self.get_script_name("pre_uninstall") or ''
        pre_uninstall_script_args = self.get_script_name("pre_uninstall") or ''

        self._write_template_file('postinst.in', {'package_name': self.get_package_name(),
                                                  'package_version': self.get_project_version__short(),
                                                  'prefix': self.get_install_prefix(),
                                                  'post_install_script_name': post_install_script_name,
                                                  'post_install_script_args': post_install_script_args,
                                                  'pre_uninstall_script_name': pre_uninstall_script_name,
                                                  'pre_uninstall_script_args': pre_uninstall_script_args,
                                                 }, '755')

        directories_to_clean = [item for item in self._directories]
        directories_to_clean.sort()
        directories_to_clean.reverse()
        self._write_template_file('prerm.in', {'package_name': self.get_package_name(),
                                               'package_version': self.get_project_version__short(),
                                               'prefix': self.get_install_prefix(),
                                               'close_on_upgrade_or_removal' : '1' if \
                                                            self.should_close_app_on_upgrade_or_removal() else '0',
                                               'post_install_script_name': post_install_script_name,
                                               'post_install_script_args': post_install_script_args,
                                               'pre_uninstall_script_name': pre_uninstall_script_name,
                                               'pre_uninstall_script_args': pre_uninstall_script_args,
                                               'directories_to_clean': ' '.join([repr(i) for i in directories_to_clean]),
                                               }, '755')
        self._write_template_file('preinst.in', {'target_arch': self.get_target_arch(),
                                                 }, '755')

    def _write_debian_directory(self):
        self._clean_debian_directory()
        self._write_templates()

