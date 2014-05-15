
from pkg_resources import resource_filename
from contextlib import contextmanager
from logging import getLogger
from . import buildout, compiler, execute, signtool

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
def temporary_directory_context():
    from tempfile import mkdtemp
    from shutil import rmtree
    tempdir = mkdtemp()
    with chdir(tempdir):
        yield tempdir
    rmtree(tempdir, ignore_errors=True)

def _get_install_package_verion(package_name):
    import pkg_resources
    pkg_info = pkg_resources.get_distribution(package_name)
    return pkg_info.version

def get_pypi_index_url():
    from ConfigParser import ConfigParser, NoOptionError, NoSectionError
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

def _get_package_url(package_name):
    import pkg_resources
    from infi.pypi_manager import DjangoPyPI, PyPI
    pypi_url = get_pypi_index_url().replace("/simple", "")
    pkg_info = pkg_resources.get_distribution(package_name)
    pypi = PyPI() if is_official_pypi(pypi_url) else DjangoPyPI(pypi_url)
    return pypi.get_source_distribution_url_of_specific_release_version(package_name, pkg_info.version).split("#")[0]

def download_buildout(destination_dir):
    from urllib import urlretrieve
    buildout_url = _get_package_url("zc.buildout")
    buildout_filepath = buildout_url.split('/')[-1]
    with chdir(destination_dir):
        urlretrieve(buildout_url, buildout_filepath)

def write_ez_setup_py(destination_dir):
    with chdir(destination_dir):
        with open(ez_setup_txt) as fd:
            content = fd.read()
        content = content.replace("0.8", _get_install_package_verion("setuptools"))
        content = content.replace("https://pypi.python.org/packages/source/s/setuptools/", ".cache/dist/")
        with open("ez_setup.py", "w") as fd:
            fd.write(content)

def download_distribute(destination_dir):
    from urllib import urlretrieve
    distribute_url = _get_package_url("distribute")
    distribute_filepath = distribute_url.split('/')[-1]
    with chdir(destination_dir):
        urlretrieve(distribute_url, distribute_filepath)

def download_setuptools(destination_dir):
    from urllib import urlretrieve
    distribute_url = _get_package_url("setuptools")
    distribute_filepath = distribute_url.split('/')[-1]
    with chdir(destination_dir):
        urlretrieve(distribute_url, distribute_filepath)
    write_ez_setup_py(destination_dir)

def download_package_source(package_name, destination_dir):
    from urllib import urlretrieve
    url = _get_package_url(package_name)
    filepath = url.split('/')[-1]
    with chdir(destination_dir):
        urlretrieve(url, filepath)
    return filepath

def get_dependencies(name):
    from pkg_resources import get_distribution
    from collections import deque
    distribution = get_distribution(name)
    queue = deque()
    queue.extend(distribution.requires())
    dependencies = set()
    while queue:
        depenency = queue.popleft().project_name
        if depenency in dependencies:
            continue
        dependencies.add(depenency)
        queue.extend(get_distribution(depenency).requires())
    return dependencies

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
