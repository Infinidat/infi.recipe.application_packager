from zc.buildout.download import Download
from logging import getLogger
logger = getLogger(__name__)

RECIPE_DEFAULTS = {'dependent-scripts': 'true',
                   'eggs': '',
                   'scripts': '',
                   'deb-dependencies': '',
                   'sign-executables-and-msi': 'false',
                   'pfx-file': '~/.authenticode/certificate.pfx',
                   'pfx-password-file': '~/.authenticode/certificate-password.txt',
                   'timestamp-url':  "http://timestamp.verisign.com/scripts/timstamp.dll",
                   'add-remove-programs-icon': None,
                   'msi-banner-bmp': None,
                   'msi-dialog-bmp': None,
                  }

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

    def get_download_cache_dist(self):
        from os import path
        return path.join(self.get_download_cache(), "dist")

    def get_eggs_directory(self):
        return self.get_buildout_section().get("eggs-directory")

    def get_buildout_dir(self):
        return self.get_buildout_section().get('directory')

    def get_project_version__short(self):
        from pkg_resources import parse_version
        version_numbers = []
        parsed_version = list(parse_version(self.get_project_version__long()))
        for item in parsed_version:
            if not item.isdigit():
                break
            version_numbers.append(int(item))
        while len(version_numbers) < 3:
            version_numbers.append(0)
        index = parsed_version.index(item)
        for item in parsed_version[index:]:
            if item.isdigit():
                version_numbers.append(int(item))
                break
        return '.'.join([str(item) for item in  version_numbers])

    def get_project_version__long(self):
        from os import path
        with open(path.join(self.get_buildout_dir(), self.get_project_section().get('version_file'))) as fd:
            exec fd.read()
            return locals()['__version__']

    def get_working_directory(self):
        from os import path
        return path.join(self.get_buildout_dir(), 'parts')

    def _get_recipe_atribute(self, attribute):
        return self.get_recipe_section().get(attribute, RECIPE_DEFAULTS[attribute])

    def get_dependent_scripts(self):
        return self._get_recipe_atribute("dependent-scripts")

    def get_eggs_for_production(self):
        return self._get_recipe_atribute("eggs")

    def get_scripts_for_production(self):
        return self._get_recipe_atribute("scripts")

    def get_deb_dependencies(self):
        return self._get_recipe_atribute("deb-dependencies")

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

    def get_platform_arch(self):
        from platform import system, linux_distribution
        from sys import maxsize
        is_64 = maxsize > 2 ** 32
        distribution_name, _, _ = linux_distribution()
        is_redhat_or_centos = distribution_name.lower().startswith('red') or distribution_name.lower().startswith('cent')
        arch_by_distro = {''}
        arch_by_os = {
                      "Windows": 'x64' if is_64 else 'x86',
                      "Linux": ('x86_64' if is_redhat_or_centos else 'amd64') if is_64 else \
                               ('i686' if is_redhat_or_centos else 'i386'),
                     }
        return arch_by_os.get(system())

    def get_install_dir(self):
        from os import path
        return path.join(r'C:\Program Files', self.get_company_name(), self.get_product_name())

    def get_install_prefix(self):
        return "/opt/{}/{}".format(self.get_company_name().lower(), self.get_project_name())

    def get_os_string(self):
        from platform import architecture, system, linux_distribution
        from sys import maxsize
        is_64 = maxsize > 2 ** 32
        arch_name = 'x64' if is_64 else 'x86'
        system_name = system().lower().replace('-', '').replace('_', '')
        distribution_name, distribution_version, _ = linux_distribution()
        distribution_name = distribution_name.lower()
        is_ubuntu = distribution_name == 'ubuntu'
        distribution_version = distribution_version.lower() if is_ubuntu else distribution_version.lower().split('.')[0]
        string_by_os = {
                        "Windows": '-'.join([system_name, arch_name]),
                        "Linux": '-'.join([system_name, distribution_name, distribution_version, arch_name]),
        }
        return string_by_os.get(system())

    def get_script_name(self, key):
        return self.get_project_section().get('{}_script_name'.format(key), None)

    def get_script_args(self, key):
        return self.get_project_section().get('{}_script_args'.format(key), '')

    def should_sign_files(self):
        key = 'sign-executables-and-msi'
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
        resource_file = self.get_recipe_section().get(name, None)
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

    def write_buildout_configuration_file_for_production(self):
        from .. import utils, assertions
        method = utils.buildout.write_buildout_configuration_file_for_production
        return method(self.get_dependent_scripts(),
                      self.get_eggs_for_production() or self.get_python_module_name(),
                      self.get_scripts_for_production())