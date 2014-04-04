__import__("pkg_resources").declare_namespace(__name__)

from logging import getLogger
from ..base import PackagingRecipe, RECIPE_DEFAULTS
from .. import utils
from os import path, curdir, makedirs, listdir, remove
from shutil import rmtree, copy
from pkg_resources import resource_filename

logger = getLogger(__name__)

SPEC_TEMPLATE = resource_filename(__name__, 'rpmspec.in')

class Recipe(PackagingRecipe):
    def install(self):
        with self.with_most_mortem():
            self.delete_non_production_packages_from_cache_dist()
            self.write_buildout_configuration_file_for_production()
            utils.compiler.compile_binary_distributions(self.get_buildout_dir(),
                                                        self.get_download_cache_dist(),
                                                        self.get_eggs_directory())
            utils.download_buildout(self.get_download_cache_dist())
            utils.download_setuptools(self.get_download_cache_dist())
            package = self.build_package()
            logger.debug("Built {}".format(package))
            return [package, ]

    def build_package(self):
        from re import search
        self._template = self._get_content_from_template()
        self._files = set()
        self._directories = set()
        self._directories_to_clean = set()

        with utils.temporary_directory_context() as tempdir:
            self._buildroot = tempdir
            self._put_all_files()
            self._inject_product_properties_to_spec()
            with utils.chdir(self.get_working_directory()):
                specfile = 'rpm.spec'
                with open(specfile, 'w') as fd:
                    fd.write(self._content)
                output = self._call_rpmbuild(specfile)
                rpm_wrote = search("Wrote: (.*)", output).groups()[0]
                if path.exists(self.rpm_filepath):
                    remove(self.rpm_filepath)
                copy(rpm_wrote, self.rpm_filepath)
            return self.rpm_filepath

    def _get_content_from_template(self):
        from string import Template
        with open(SPEC_TEMPLATE) as fd:
            return Template(fd.read())

    def _mkdir(self, name, parent_directory, just_add_it=False):
        dst = path.join(parent_directory, name)
        src = "{}{}/{}".format(self._buildroot, parent_directory, name)
        self._directories.add(dst) if not just_add_it else None
        self._directories_to_clean.add(dst)
        makedirs(src) if not just_add_it else None
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
        buildroot_filepath = "{}{}/{}".format(self._buildroot, destination_directory, destination_filename)
        destination_filepath = path.join(destination_directory, destination_filename)
        copy(source_filepath, buildroot_filepath)
        self._files.add(destination_filepath)

    def _get_requires_declaration(self):
        rpm_dependencies = self.get_recipe_section().get("rpm-dependencies", RECIPE_DEFAULTS["rpm-dependencies"])
        deps = [item.strip() for item in rpm_dependencies.splitlines()]
        return "\n".join(["Requires: {}".format(dep) for dep in deps])

    def _inject_product_properties_to_spec(self):
        directories_to_clean = [item for item in self._directories_to_clean]
        directories_to_clean.sort()
        directories_to_clean.reverse()

        kwargs = {
                  'product_name': self.get_product_name(),
                  'product_description': self.get_description(),
                  'package_name': self.get_package_name(),
                  'package_version': self.get_project_version__short(),
                  'package_arch': self.get_platform_arch(),
                  'requires_declaration': self._get_requires_declaration(),
                  'prefix': self.get_install_prefix(),
                  'build_root': self._buildroot,
                  'post_install_script_name': self.get_script_name("post_install") or "''",
                  'pre_uninstall_script_name': self.get_script_name("pre_uninstall") or "''",
                  'files': "\n".join(self._files),
                  'directories': "\n".join(["%dir {}/".format(item) for item in self._directories]),
                  'directories_to_clean': ' '.join(directories_to_clean),
                  }
        post_install_script_args = self.get_script_args("post_install")
        pre_uninstall_script_args = self.get_script_args("pre_uninstall")
        kwargs['post_install_script_args_definition'] = \
                "%define post_install_script_args {}".format(post_install_script_args) if post_install_script_args \
                else ''
        kwargs['pre_uninstall_script_args_definition'] = \
            "%define pre_uninstall_script_args {}".format(pre_uninstall_script_args) if pre_uninstall_script_args \
            else ''
        self._content = self._template.substitute(kwargs)

    def _put_all_files(self):
        makedirs("{}{}".format(self._buildroot, self.get_install_prefix()))
        self._mkdir(self.get_install_prefix(), path.sep, True)
        self._add_file('bootstrap.py', self.get_install_prefix())
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

    def get_rpm_filename(self):
        return "{}-{}-{}.rpm".format(self.get_package_name(), self.get_project_version__long(),
                                     self.get_os_string())

    @property
    def rpm_filepath(self):
        return path.join(self.get_working_directory(), self.get_rpm_filename())

    def _call_rpmbuild(self, specfile):
        return utils.execute.execute_assert_success(['rpmbuild', '--verbose', '--buildroot', self._buildroot, '-bb', specfile]).get_stdout()
