from infi.execute import execute
import os
import glob
import logging
import shutil
import platform
import hashlib
import stat

from contextlib import contextmanager
try:
    from ConfigParser import ConfigParser, NoOptionError
except:
    from configparser import ConfigParser, NoOptionError

from tempfile import NamedTemporaryFile


log = logging.getLogger(__name__)

INSTALLER_USERDATA = os.path.join('SOFTWARE', 'Microsoft', 'Windows', 'CurrentVersion', 'Installer', 'UserData')
PYPI_HOSTS = ["127.0.0.1    pypi.infinidat.com",
              "127.0.0.1    pypi",
              "127.0.0.1    pypi.python.org", ]

HOSTS_FILE = os.path.join('/', 'etc', 'hosts') if os.name != 'nt' else \
             os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "Drivers", "etc", "hosts")
CHMOD_755 = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH

from infi.recipe.application_packager.utils.execute import execute_assert_success


def get_pypi_addresses():
    """:returns: a list of PyPI addresses being looked by easy_install and buildout"""
    # TODO get the real list from pydistutils.cfg and buildout/default.cfg
    return PYPI_HOSTS

@contextmanager
def prevent_access_to_pypi_servers():
    with open(HOSTS_FILE, 'r') as fd:
        content = fd.read()
    try:
        new_content = '\n'.join([content] + get_pypi_addresses())
        with open(HOSTS_FILE, 'w') as fd:
            fd.write(new_content)
        log.info("Preventing access to pypi servers")
        log.debug("Wrote {!r} to hosts file {}".format(new_content, HOSTS_FILE))
        yield
    finally:
        with open(HOSTS_FILE, 'w') as fd:
            fd.write(content)
        log.info("Restoring access to pypi servers")
        log.debug("Wrote original content {!r} for hosts file".format(content, HOSTS_FILE))

@contextmanager
def prevent_access_to_gcc():
    from tempfile import mkdtemp
    original_path = os.environ['PATH']
    tempdir = mkdtemp('gcc')
    fake_gcc = os.path.join(tempdir, 'gcc')
    with open(fake_gcc, 'w') as fd:
        fd.write("#!/bin/sh\nexit 1")
    os.chmod(fake_gcc, CHMOD_755)
    try:
        os.environ['PATH'] = os.path.pathsep.join([tempdir, os.environ['PATH'], tempdir])
        log.info("Preventing access to gcc")
        log.debug("Setting PATH to {}".format(os.environ['PATH']))
        yield
    finally:
        os.environ['PATH'] = original_path
        log.debug("Restored PATH to {}".format(os.environ['PATH']))

class Installer(object):
    package_extension = None
    targetdir = None
    executable_extension = None

    def __init__(self, buildout_path='buildout.cfg'):
        super(Installer, self).__init__()
        self._buildout_path = os.path.abspath(buildout_path)
        self._project_dir = os.path.dirname(self._buildout_path)
        self._parser = ConfigParser()
        self._parser.read(self._buildout_path)

    @property
    def product_name(self):
        try:
            return self._parser.get('project', 'product_name')
        except NoOptionError:
            return self._parser.get('project', 'name')

    @property
    def project_name(self):
        return self.product_name.replace(' ', '-').replace('_', '-').lower()

    @property
    def package_name(self):
        return self.project_name

    @property
    def company(self):
        try:
            return self._parser.get('project', 'company')
        except NoOptionError:
            return self._parser.get('project', 'None')

    @property
    def targetdir(self):
        if os.name == 'nt':
            return os.path.join(r'C:\Program Files', self.company, self.product_name)
        return os.path.join(os.path.sep, 'opt', self.company.lower(), self.project_name)


    def _format_executable(self, executable):
        return "{}.{}".format(executable, self.executable_extension) if self.executable_extension else executable

    def has_bootstrap_ocurred(self):
        buildout_path = os.path.join(self.targetdir, 'bin', self._format_executable('buildout'))
        buildout_exists = os.path.exists(buildout_path)
        log.debug("{!r} exists: {}".format(buildout_path, buildout_exists))
        return buildout_exists

    def are_there_remainings_of_previous_installations(self):
        if os.path.exists(self.targetdir):
            log.info("Files and directories under {!r}: {!r}".format(self.targetdir, os.listdir(self.targetdir)))
        return os.path.exists(self.targetdir)

    def is_package_exists(self):
        return len(self._get_packages()) > 0

    def _get_packages(self):
        packages = glob.glob(os.path.join(self._project_dir, 'parts', '*.{}'.format(self.package_extension)))
        log.info("Found the following packages: {!r}".format(packages))
        return packages

    def get_package(self):
        return self._get_packages()[0]

    def create_package(self):
        from ..utils import chdir
        with chdir(os.path.dirname(self._buildout_path)):
            python = os.path.join('bin', 'python{}'.format('.exe' if os.name == 'nt' else ''))
            buildout_script = os.path.join('bin', 'buildout{}'.format('-script.py' if os.name == 'nt' else ''))
            stdout = execute_assert_success([python, buildout_script, '-v', 'install', 'pack']).get_stdout()
            log.debug('package created, stdout: {}'.format(stdout))

    def is_product_installed(self):
        raise NotImplementedError()

    def install_package(self, with_custom_actions=True):
        raise NotImplementedError()

    def uninstall_package(self, with_custom_actions=True):
        raise NotImplementedError()


class MsiInstaller(Installer):
    package_extension = 'msi'
    executable_extension = 'exe'

    @property
    def package_code(self):
        return self._parser.get('project', 'upgrade_code')

    @property
    def package_code_formatted(self):
        return self.package_code.strip('{}').replace('-', '').upper()

    def _get_installed_product_from_registry(self):
        from infi.registry import LocalComputer
        registry = LocalComputer()
        userdata = registry.local_machine[INSTALLER_USERDATA]
        for user in filter(lambda user: user.has_key(os.path.join('Products')), userdata.values()):
            for product in user['Products'].values():
                display_name = product['InstallProperties'].values_store['DisplayName'].to_python_object()
                log.debug("product found: {!r}".format(display_name))
                if display_name == self.product_name:
                    log.debug("Product is indeed installed")
                    return product
        log.debug("Product is not installed")
        return None

    def is_product_installed(self):
        return self._get_installed_product_from_registry() is not None

    def install_package(self, with_custom_actions=True):
        logfile = self.get_package() + '.install.log'
        with open(logfile, 'w'):
            pass
        args = ['msiexec', '/i', self.get_package(), '/passive', '/l*vx', logfile]
        if not with_custom_actions:
            args.append("NO_CUSTOM_ACTIONS=1")
        with prevent_access_to_pypi_servers():
            try:
                execute_assert_success(args)
            finally:
                with open(logfile) as fd:
                    print(fd.read())

    def uninstall_package(self, with_custom_actions=True):
        logfile = self.get_package() + '.uninstall.log'
        with open(logfile, 'w'):
            pass
        properties = self._get_installed_product_from_registry()['InstallProperties'].values_store
        uninstall_string = properties['UninstallString'].to_python_object()
        args = uninstall_string.split() + ['/passive', '/l*vx', logfile]
        if not with_custom_actions:
            args.append("NO_CUSTOM_ACTIONS=1")
        try:
            execute_assert_success(args)
        finally:
            with open(logfile) as fd:
                print(fd.read())


class RpmInstaller(Installer):
    package_extension = 'rpm'

    def is_product_installed(self):
        pid = execute_assert_success(['rpm', '-q', self.package_name], allowed_return_codes=[0, 1])
        output = pid.get_stderr() + pid.get_stdout()
        return 'not installed' not in output

    def install_package(self, with_custom_actions=True):
        env = os.environ.copy()
        if not with_custom_actions:
            env['NO_CUSTOM_ACTIONS'] = '1'
        with prevent_access_to_pypi_servers(), prevent_access_to_gcc():
            execute_assert_success(['rpm', '-Uvh', self.get_package()], env=env)

    def uninstall_package(self, with_custom_actions=True):
        env = os.environ.copy()
        if not with_custom_actions:
            env['NO_CUSTOM_ACTIONS'] = '1'
        execute_assert_success(['rpm', '-e', self.package_name], env=env)


class DebInstaller(Installer):
    package_extension = 'deb'

    def is_product_installed(self):
        output = execute_assert_success(["dpkg", "--list", self.package_name], allowed_return_codes=[0, 1]).get_stdout().splitlines()
        return any([line.startswith(b'ii') and self.package_name in line.decode('ascii') for line in output])

    def install_package(self, with_custom_actions=True):
        env = os.environ.copy()
        if not with_custom_actions:
            env['NO_CUSTOM_ACTIONS'] = '1'
        with prevent_access_to_pypi_servers(), prevent_access_to_gcc():
            execute_assert_success(['dpkg', '-i', self.get_package()], env=env)

    def uninstall_package(self, with_custom_actions=True):
        env = os.environ.copy()
        if not with_custom_actions:
            env['NO_CUSTOM_ACTIONS'] = '1'
        execute_assert_success(['dpkg', '-r', self.package_name], env=env)


class PkgInstaller(Installer):
    package_extension = 'pkg.gz'

    def __init__(self, *args, **kwargs):
        super(PkgInstaller, self).__init__(*args, **kwargs)
        admin_file_content = '\n'.join(['partial=nocheck',
                                    'runlevel=nocheck',
                                    'idepend=nocheck',
                                    'rdepend=nocheck',
                                    'setuid=nocheck',
                                    'action=nocheck',
                                    'partial=nocheck',
                                    'conflict=nocheck',
                                    'authentication=quit',
                                    'instance=overwrite',
                                    'basedir=default'])
        self.admin_file = NamedTemporaryFile(mode='w')
        self.admin_file.write(admin_file_content)
        self.admin_file.flush()
        os.fsync(self.admin_file.fileno())

    def is_product_installed(self):
        return 0 == execute(["pkginfo", self.package_name]).get_returncode()

    def install_package(self, with_custom_actions=True):
        response_file = NamedTemporaryFile(mode='w')
        response_file.write("NO_CUSTOM_ACTIONS={}".format(int(not with_custom_actions)))
        response_file.flush()
        os.fsync(response_file.fileno())
        with prevent_access_to_pypi_servers(), prevent_access_to_gcc():
            zipped_package_name = self.get_package()
            unzipped_package_name = zipped_package_name[:-3]
            execute_assert_success('gunzip -c {} > {}'.format(zipped_package_name, unzipped_package_name), shell=True)
            execute_assert_success(['pkgadd',
                                    '-n',
                                    '-a', self.admin_file.name,
                                    '-r', response_file.name,
                                    '-d', unzipped_package_name,
                                    self.package_name])

    def uninstall_package(self, with_custom_actions=True):
        # with_custom_actions is actually ignored here. This flag is passed to the installer through the response file.
        # Luckily, the preremove scripts also gets this info (it's saved somwhere in the os until the removal)
        execute_assert_success(['pkgrm', '-n', '-a', self.admin_file.name, self.package_name], allowed_return_codes=[0,])
