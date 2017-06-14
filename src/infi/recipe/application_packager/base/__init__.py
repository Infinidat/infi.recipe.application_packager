from contextlib import contextmanager
from infi.recipe.application_packager import utils
from zc.buildout.download import Download
from logging import getLogger
logger = getLogger(__name__)

RECIPE_DEFAULTS = {'require-administrative-privileges': 'false',
                   'require-administrative-privileges-gui': 'false',
                   'dependent-scripts': 'false',
                   'minimal-packages': '',
                   'shrink-cache-dist': 'true',
                   'eggs': '',
                   'scripts': '',
                   'gui-scripts': '',
                   'deb-dependencies': '',
                   'rpm-dependencies': '',
                   'sign-executables-and-msi': 'false',
                   'pfx-file': '~/.authenticode/certificate.pfx',
                   'pfx-password-file': '~/.authenticode/certificate-password.txt',
                   'timestamp-url':  "http://timestamp.verisign.com/scripts/timstamp.dll",
                   'add-remove-programs-icon': "~/.msi-ui/icon.ico",
                   'shortcuts-icon': "~/.msi-ui/icon.exe",
                   'msi-banner-bmp': "~/.msi-ui/WixUIBanner.bmp",
                   'msi-dialog-bmp': "~/.msi-ui/WixUIDialog.bmp",
                   'startmenu-shortcuts': '[]',
                   'eula-rtf': None,
                   'documentation-url': None,
                   '_target_arch': None,
                   'close-on-upgrade-or-removal' : 'true',
                   'additional-directories': '[]'
                  }

PYTHON_PACKAGES_USED_BY_PACKAGING = ["infi.recipe.buildout_logging",
                                     "infi.recipe.console_scripts",
                                     "infi.recipe.close_application",
                                     "zc.buildout",
                                     "pip",
                                     "setuptools",
                                     "pythonpy",
                                     "buildout.wheel"]

SCRIPTS_BY_PACKAGING = ["buildout"]


class PackagingRecipe(object):
    def __init__(self, buildout, name, options):
        super(PackagingRecipe, self).__init__()
        self.buildout = buildout
        self.options = options
        self.downloader = Download(buildout)

    def install(self): # pragma: no cover
        raise NotImplementedError()

    def update(self): # pragma: no cover
        return self.install()

    def get_buildout_section(self):
        return self.buildout.get('buildout')

    def get_project_section(self):
        return self.buildout.get('project')

    def get_recipe_section(self):
        return self.options

    def get_download_cache(self):
        return self.get_buildout_section().get("download-cache")

    def get_buildout_extensions(self):
        return self.get_buildout_section().get("extensions")

    def using_wheels(self):
        return self.get_buildout_extensions() and 'buildout.wheel' in self.get_buildout_extensions()

    def get_download_cache_dist(self):
        from os import path
        return path.join(self.get_download_cache(), "dist")

    def get_eggs_directory(self):
        return self.get_buildout_section().get("eggs-directory")

    def get_buildout_dir(self):
        return self.get_buildout_section().get('directory')

    def get_project_version__short(self):
        from infi.os_info import shorten_version_string
        return shorten_version_string(self.get_project_version__long())

    def get_project_version__long(self):
        from infi.os_info import get_version_from_file
        from os import path
        filepath = path.join(self.get_buildout_dir(), self.get_project_section().get('version_file'))
        return get_version_from_file(filepath)

    def get_working_directory(self):
        from os import path
        return path.join(self.get_buildout_dir(), 'parts')

    def _get_recipe_atribute(self, attribute):
        return self.get_recipe_section().get(attribute, RECIPE_DEFAULTS[attribute])

    def get_dependent_scripts(self):
        return self._get_recipe_atribute("dependent-scripts")

    def get_minimal_packages(self):
        return self._get_recipe_atribute("minimal-packages")

    def get_eggs_for_production(self):
        return self._get_recipe_atribute("eggs").strip()

    def get_console_scripts_for_production(self):
        return self._get_recipe_atribute("scripts")

    def get_gui_scripts_for_production(self):
        return self._get_recipe_atribute("gui-scripts")

    def get_require_administrative_privileges(self):
        return self._get_recipe_atribute("require-administrative-privileges")

    def get_require_administrative_privileges_gui(self):
        return self._get_recipe_atribute("require-administrative-privileges-gui")

    def get_deb_dependencies(self):
        return self._get_recipe_atribute("deb-dependencies")

    def should_close_app_on_upgrade_or_removal(self):
        key = 'close-on-upgrade-or-removal'
        return self.get_recipe_section().get(key, RECIPE_DEFAULTS[key]) in [True, 'true', 'True']

    def get_product_name(self):
        return self.get_project_section().get('product_name', self.get_project_section().get('name'))

    def get_project_name(self):
        return self.get_product_name().replace(' ', '-').replace('_', '-').lower()

    def get_package_name(self):
        return self.get_project_name()

    def get_python_module_name(self):
        return self.get_project_section().get('name')

    def get_company_name(self):
        company = self.get_project_section().get('company', 'None')
        if company in [None, 'None', 'none']: # pragma: no cover
            logger.error("Section [project] is missing an attribute 'company'")
            raise AssertionError()
        return company

    def get_upgrade_code(self):
        upgrade_code = self.get_project_section().get('upgrade_code')
        if upgrade_code in [None, 'None', 'none']: # pragma: no cover
            logger.error("Section [project] is missing an attribute 'upgrade_code'")
            raise AssertionError()
        return upgrade_code.upper()

    def get_description(self):
        return self.get_project_section().get('long_description')

    def get_documentation_url(self):
        return self._get_recipe_atribute('documentation-url')

    def get_platform_arch(self):
        from platform import system, dist, processor
        from sys import maxsize
        is_64 = maxsize > 2 ** 32
        distribution_name, _, _ = dist()
        is_rpm = any(distribution_name.lower().startswith(x) for x in ['red', 'cent', 'suse'])
        arch_by_distro = {''}
        arch_by_os = {
                      "Windows": 'x64' if is_64 else 'x86',
                      "Linux": ('ppc64le' if is_rpm else 'ppc64el') if processor() == 'ppc64le' else \
                               ('ppc64' if is_rpm else 'powerpc') if processor() == 'ppc64' else \
                               ('x86_64' if is_rpm else 'amd64') if is_64 else \
                               ('i686' if is_rpm else 'i386'),
                      "SunOS": 'sparc' if 'sparc' == processor() else ('amd64' if is_64 else 'i386'),
                      "AIX": "ppc",
                     }
        return arch_by_os.get(system())

    def get_target_arch(self):
        return self._get_recipe_atribute('_target_arch') or self.get_platform_arch()

    def get_install_dir(self):
        from os import path
        return path.join(r'C:\Program Files', self.get_company_name(), self.get_product_name())

    def get_install_prefix(self):
        return "/opt/{}/{}".format(self.get_company_name().lower(), self.get_project_name())

    def _get_centos_dist_name(self):
        from os import path
        # RedHat hosts have /etc/centos-release file, but with RedHat... written inside
        # python-2.7 thinks its centos just because this file exists
        CENTOS_FILE = path.join(path.sep, "etc", "centos-release")
        with open(CENTOS_FILE) as fd:
            content = fd.read()
        if content.startswith("Red"):
            return "redhat"
        return content.split()[0].lower()

    def get_os_string(self):
        from infi.os_info import get_platform_string
        return get_platform_string()

    def get_script_name(self, key):
        return self.get_project_section().get('{}_script_name'.format(key), None)

    def get_script_args(self, key):
        return self.get_project_section().get('{}_script_args'.format(key), '')

    def should_sign_files(self):
        from os import name
        key = 'sign-executables-and-msi'
        return self.get_recipe_section().get(key, RECIPE_DEFAULTS[key]) in [True, 'true', 'True'] and name == "nt"

    def should_shrink_cache_dist(self):
        key = 'shrink-cache-dist'
        return self.get_recipe_section().get(key, RECIPE_DEFAULTS[key]) in [True, 'true', 'True']

    def get_pfx_file(self):
        from os.path import normpath, expanduser
        key = 'pfx-file'
        return normpath(expanduser(self.get_recipe_section().get(key, RECIPE_DEFAULTS[key])))

    def get_pfx_password_file(self):
        from os.path import normpath, expanduser
        key = 'pfx-password-file'
        return normpath(expanduser(self.get_recipe_section().get(key, RECIPE_DEFAULTS[key])))

    def _get_resource_file_from_recipe_section(self, name):
        from os.path import exists, expanduser, abspath
        resource_file = self.get_recipe_section().get(name, RECIPE_DEFAULTS.get(name, None))
        if resource_file is None:
            return None
        resource_file = abspath(expanduser(resource_file))
        return resource_file if exists(resource_file) else None

    def get_add_remove_programs_icon(self):
        return self._get_resource_file_from_recipe_section('add-remove-programs-icon')

    def get_msi_banner_bmp(self):
        return self._get_resource_file_from_recipe_section('msi-banner-bmp')

    def get_msi_dialog_bmp(self):
        return self._get_resource_file_from_recipe_section('msi-dialog-bmp')

    def get_eula_rtf(self):
        return self._get_resource_file_from_recipe_section('eula-rtf')

    def get_shortcuts_icon(self):
        return self._get_resource_file_from_recipe_section("shortcuts-icon")

    def get_startmenu_shortcuts(self):
        return self._get_recipe_atribute("startmenu-shortcuts")

    def get_additional_directories(slef):
        return slef._get_recipe_atribute("additional-directories")

    def write_bootstrap_for_production(self):
        from ..utils.buildout import write_bootstrap_for_production
        write_bootstrap_for_production()

    def write_get_pip_for_production(self):
        from ..utils.buildout import write_get_pip_for_production
        write_get_pip_for_production()

    def write_buildout_configuration_file_for_production(self):
        from .. import utils, assertions
        method = utils.buildout.write_buildout_configuration_file_for_production
        eggs = self.get_eggs_for_production() or self.get_python_module_name()
        eggs = "\n".join(eggs.split() + PYTHON_PACKAGES_USED_BY_PACKAGING)
        scripts = self.get_console_scripts_for_production()
        if scripts:
            scripts = "\n".join(scripts.split() + SCRIPTS_BY_PACKAGING)
        return method(self.get_dependent_scripts(), self.get_minimal_packages(),
                      eggs,
                      scripts,
                      self.get_gui_scripts_for_production(),
                      self.get_require_administrative_privileges(),
                      self.get_require_administrative_privileges_gui(),
                      self.get_buildout_extensions())

    def download_python_packages_used_by_packaging(self, source=None):
        packages = self.get_python_packages_used_by_packaging()
        for package in packages:
            self.download_python_package_to_cache_dist(package, source)

    def get_python_packages_used_by_packaging(self):
        from ..utils import get_dependencies
        packages = set()
        for package in PYTHON_PACKAGES_USED_BY_PACKAGING:
            packages |= set([package])
            packages |= set(get_dependencies(package))
        return packages

    def download_python_package_to_cache_dist(self, package_name, source=None):
        import pkg_resources
        pkg_info = pkg_resources.get_distribution(package_name)
        pkg_info.as_requirement()
        installer = self._get_installer()
        installer._download_cache = None
        dist = installer._obtain(pkg_info.as_requirement(), source)
        if dist:
            return installer._fetch(dist, self.get_download_cache_dist(), None)

    def convert_python_packages_used_by_packaging_to_wheels(self):
        from infi.recipe.application_packager.utils.compiler import execute_with_isolated_python
        from glob import glob
        from os import path
        cache_dist = path.join(self.get_buildout_dir(), '.cache', 'dist')
        for package in self.get_python_packages_used_by_packaging():
            if glob(path.join(cache_dist, '{}*.whl'.format(package))):
                continue
            for egg in glob(path.join(cache_dist, '{}*.egg'.format(package))):
                execute_with_isolated_python(self.get_buildout_dir(), ['-m', 'wheel', 'convert', '--dest-dir', cache_dist, egg])

    def _get_installer(self):
        from zc.buildout.easy_install import Installer
        import sys
        dest = self.buildout['buildout']['eggs-directory']
        links = self.buildout['buildout'].get('find-links', '').split()
        index = self.buildout['buildout'].get('index')
        always_unzip = None
        path = [self.buildout['buildout']['develop-eggs-directory']]
        allow_hosts = ('*',)
        newest = True
        versions = None
        use_dependency_links = False
        check_picked = True
        installer = Installer(dest, links, index, sys.executable,
                          always_unzip, path,
                          newest, versions, use_dependency_links,
                          allow_hosts=allow_hosts,
                          check_picked=check_picked)
        return installer

    def delete_non_production_packages_from_cache_dist(self):
        from ..utils import get_dependencies, get_distributions_from_dependencies
        from glob import glob
        from os import path, remove
        if not self.should_shrink_cache_dist():
            return
        eggs = self.get_eggs_for_production().split() or [self.get_python_module_name()]
        eggs.extend(PYTHON_PACKAGES_USED_BY_PACKAGING)
        dependencies = set.union(set(eggs), *[get_dependencies(name) for name in eggs])
        distributions = get_distributions_from_dependencies(dependencies)
        for filepath in glob(path.join(self.get_download_cache_dist(), '*')):
            basename = path.basename(filepath).lower()
            if any([distname.lower() in basename and version.replace('-', '_') in basename.replace('-', '_')
                    for distname, version in distributions.items()]):
                continue
            # in the post-pep-440 era, foo-1.0-1.tar.gz is parsed as foo-1.0.post1
            if any([distname.lower() in basename and version.replace('.post', '-') in basename
                    for distname, version in distributions.items()]):
                continue
            # in the post-pep-440 era, foo-2.0.0-pre8.tar.gz is parsed as 2.0.0rc8
            if any([distname.lower() in basename and version in basename.replace('-pre', 'rc')
                    for distname, version in distributions.items()]):
                continue

            logger.info("shrinking cache-dist and removing {}".format(filepath))
            remove(filepath)

    @contextmanager
    def with_most_mortem(self):
        try:
            yield
        except:
            if self.get_recipe_section().get('pdb', 'false') == 'true':
                import pdb; pdb.post_mortem()
            raise

    def get_signtool(self):
        recipe = self.get_recipe_section()
        timestamp_url = recipe.get("timestamp-url", RECIPE_DEFAULTS['timestamp-url'])
        certificate = recipe.get("pfx-file", RECIPE_DEFAULTS['pfx-file'])
        password_file = recipe.get("pfx-password-file", RECIPE_DEFAULTS['pfx-password-file'])
        return utils.signtool.Signtool(timestamp_url, certificate, password_file)

    def add_aditional_directories(self):
        from os import path
        for d in eval(self.get_additional_directories()):
            dirname = path.dirname(d.rstrip('/\\'))
            dest_dir = path.join(self.get_install_prefix(), dirname)
            self._add_directory(path.join(self.get_buildout_dir(), d), dest_dir)
