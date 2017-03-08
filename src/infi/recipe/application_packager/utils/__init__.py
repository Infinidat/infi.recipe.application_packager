
from pkg_resources import resource_filename
from contextlib import contextmanager
from logging import getLogger
from . import buildout, compiler, execute, signtool, rcedit
try:
    from urllib import urlretrieve
except ImportError:
    from urllib.request import urlretrieve

try:
    from ConfigParser import ConfigParser, NoOptionError, NoSectionError
except ImportError:
    from configparser import ConfigParser, NoOptionError, NoSectionError


logger = getLogger(__name__)
ez_setup_txt = resource_filename(__name__, "ez_setup.txt")
BUILDOUT_PARAMETERS = []

def _chdir_and_log(path):
    from os import chdir
    chdir(path)
    logger.debug("Changed directory to {!r}".format(path))

@contextmanager
def chdir(destination_directory):
    from os import path, curdir
    destination_directory = path.abspath(destination_directory)
    current_dir = path.abspath(curdir)
    _chdir_and_log(destination_directory)
    try:
        yield
    finally:
        try:
            _chdir_and_log(current_dir)
        except:
            logger.exception("Failed to change back to directory {}".format(current_dir))

@contextmanager
def temporary_directory_context(should_chdir=True):
    from tempfile import mkdtemp
    from shutil import rmtree
    tempdir = mkdtemp()
    if should_chdir:
        with chdir(tempdir):
            yield tempdir
    else:
        yield tempdir
    rmtree(tempdir, ignore_errors=True)

def _get_install_package_verion(package_name):
    import pkg_resources
    pkg_info = pkg_resources.get_distribution(package_name)
    return pkg_info.version

def get_pypi_index_url():
    from os import path
    pydistutils_files = [path.expanduser(path.join("~", basename)) for basename in ['.pydistutils.cfg', 'pydistutils.cfg']]
    pydistutils = ConfigParser()
    pydistutils.read(pydistutils_files)
    try:
        return pydistutils.get("easy_install", "index-url").strip("/")
    except (NoSectionError, NoOptionError):
        for filepath in pydistutils_files:
            if path.exists(filepath):
                with open(filepath) as fd:
                    logger.debug("{}: {!r}".format(filepath, fd.read()))
            else:
                logger.debug("{} does not exist".format(filepath))
        return "https://pypi.python.org/simple"

def is_official_pypi(url):
    return 'python.org' in url

def write_ez_setup_py(destination_dir):
    with chdir(destination_dir):
        with open(ez_setup_txt) as fd:
            content = fd.read()
        content = content.replace("REPLACE_DEFAULT_VERSION", _get_install_package_verion("setuptools"))
        content = content.replace("REPLACE_DEFAULT_URL", ".cache/dist/")
        with open("ez_setup.py", "w") as fd:
            fd.write(content)

def get_dependencies(name):
    from pkg_resources import get_distribution
    from collections import deque
    distribution = get_distribution(name)
    queue = deque()
    queue.extend(distribution.requires())
    requirements = set()
    while queue:
        requirement = queue.popleft()
        depenency = requirement.project_name
        if requirement in requirements:
            continue
        requirements.add(requirement)
        queue.extend(get_distribution(depenency).requires(extras=requirement.extras))
    return {requirement.project_name for requirement in requirements}

def get_distributions_from_dependencies(dependencies):
    """:returns a dict of {distname:version}"""
    from pkg_resources import get_distribution
    get_distname = lambda dist: dist.egg_name().split('-')[0]
    get_version = lambda dist: dist.version.lower()
    distributions = dict()
    for dependency in dependencies:
        distribution = get_distribution(dependency)
        version = get_version(distribution)
        # adding both solves two problems:
        # * git-py is saved as git_py
        # * egg_name for Archive on windows is archive
        distributions[get_distname(distribution)] = version
        distributions[dependency] = version
    return distributions
