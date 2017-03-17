__import__("pkg_resources").declare_namespace(__name__)


from logging import getLogger
from ..base import PackagingRecipe, RECIPE_DEFAULTS
from .. import utils
from os import path, curdir, makedirs, listdir, walk, stat, remove
from shutil import copy
from pkg_resources import resource_filename


logger = getLogger(__name__)


PROTOTYPE_FILENAME = 'Prototype'
PKGINFO_FILENAME = 'pkginfo'
PREINST_FILENAME = 'preinstall'
POSTINST_FILENAME = 'postinstall'
PREUNINST_FILENAME = 'preremove'


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
        with utils.temporary_directory_context(should_chdir=True) as cur_dir:
            with utils.temporary_directory_context(should_chdir=False) as output_dir:
                self._put_all_files()
                self._write_working_directory()
                self._make_pkg_as_fs_stream(cur_dir, output_dir)
                self._translate_pkg_to_file_stream(output_dir, self._get_pkg_filepath(), self.get_package_name())
                self._compress_package(self._get_pkg_filepath())
                return self._get_pkg_gz_filepath()

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

    def _get_pkg_filename(self):
        return "{}-{}-{}.pkg".format(self.get_package_name(), self.get_project_version__long(), self.get_os_string())

    def _get_pkg_filepath(self):
        return path.join(self.get_working_directory(), self._get_pkg_filename())

    def _get_pkg_gz_filepath(self):
        return self._get_pkg_filepath() + '.gz'

    def _make_pkg_as_fs_stream(self, src_dir, out_dir):
        utils.execute.execute_assert_success(['pkgmk', '-o', '-r', path.abspath(src_dir),
                                                     '-d', out_dir, '-f', PROTOTYPE_FILENAME])

    def _translate_pkg_to_file_stream(self, src_fs, dst_filename, package_name):
        utils.execute.execute_assert_success(
            ['pkgtrans', '-s', src_fs, dst_filename, package_name])

    def _compress_package(self, pkg_filename):
        utils.execute.execute_assert_success(
            ['gzip', '-9', '-f', pkg_filename])

    def _write_template_file(self, filename, formatting_dict, permissions='644'):
        from string import Template
        src = resource_filename(__name__, filename + '.in')
        dst = path.join(curdir, filename)
        with open(src, 'r') as fd:
            template = Template(fd.read())
        with open(dst, 'w') as fd:
            fd.write(template.substitute(formatting_dict))
            utils.execute.execute_assert_success("chmod {} {}".format(permissions, dst).split())

    def _write_prototype_file(self):
        def write_line(elements):
            fd.write(' '.join(elements) + '\n')

        dst_filename = path.abspath(path.join(curdir, PROTOTYPE_FILENAME))
        with open(dst_filename, 'w') as fd:
            write_line(['i', PKGINFO_FILENAME])
            write_line(['i', PREINST_FILENAME])
            write_line(['i', POSTINST_FILENAME])
            write_line(['i', PREUNINST_FILENAME])
            walk_root = path.abspath(curdir)
            for root, dirnames, pathnames in walk(walk_root):
                for f in pathnames:
                    relpath = path.join(path.sep, root[len(walk_root):], f)
                    fullpath = path.join(root, f)
                    if path.abspath(fullpath) == dst_filename:
                        continue
                    if ' ' in relpath:
                        # setuptools has filenames with spaces, and solaris pkg does not support this
                        remove(fullpath)
                        continue
                    write_line(['f', 'none', relpath, oct(stat(fullpath).st_mode)[-3:], 'root', 'root'])
                for f in dirnames:
                    relpath = path.join(path.sep, root[len(walk_root):], f)
                    fullpath = path.join(root, f)
                    write_line(['d', 'none', relpath, oct(stat(fullpath).st_mode)[-3:], 'root', 'root'])

    def _write_templates(self):
        self._write_template_file(PKGINFO_FILENAME, {'package_name': self.get_package_name(),
                                                     'package_version': self.get_project_version__short(),
                                                     'package_revision': self._get_package_revision(),
                                                     'package_arch': self.get_platform_arch(),
                                                     'company': self.get_company_name(),
                                                     'product_description': self.get_description(),
                                                      })

        post_install_script_name = self.get_script_name("post_install") or ''
        post_install_script_args = self.get_script_args("post_install") or ''
        pre_uninstall_script_name = self.get_script_name("pre_uninstall") or ''
        pre_uninstall_script_args = self.get_script_args("pre_uninstall") or ''
        self._write_template_file(POSTINST_FILENAME, {'package_name': self.get_package_name(),
                                                      'package_version': self.get_project_version__short(),
                                                      'prefix': self.get_install_prefix(),
                                                      'post_install_script_name': post_install_script_name,
                                                      'post_install_script_args': post_install_script_args,
                                                      'pre_uninstall_script_name': pre_uninstall_script_name,
                                                      'pre_uninstall_script_args': pre_uninstall_script_args,
                                                     }, '755')
        self._write_template_file(PREINST_FILENAME, {'package_name': self.get_package_name(),
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
        self._write_template_file(PREUNINST_FILENAME, {'package_name': self.get_package_name(),
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

    def _get_package_revision(self):
        from datetime import datetime
        from os import path

        _prettify = lambda date_string: date_string.split()[0].replace('-', '.')
        todays_date = datetime.now().isoformat(' ')
        filepath = path.join(self.get_buildout_dir(), self.get_project_section().get('version_file'))

        try:
            with open(filepath) as fd:
                exec(fd.read())
                return _prettify(locals()['git_commit_date'])
        except:
            return _prettify(todays_date)

    def _write_working_directory(self):
        self._write_prototype_file()
        self._write_templates()

