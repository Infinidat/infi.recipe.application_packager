
from contextlib import contextmanager
from logging import getLogger
from . import buildout, compiler, execute, signtool

logger = getLogger(__name__)

BUILDOUT_PARAMETERS = ['-s']

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

def download_buildout(destination_dir):
    from urllib import urlretrieve
    from infi.pypi_manager import PyPI
    pypi = PyPI()
    versions_1_x = [version for version in pypi.get_available_versions("zc.buildout")
                    if version.startswith('1.')]
    buildout_url = pypi.get_source_distribution_url_of_specific_release_version("zc.buildout", versions_1_x[0])
    buildout_filepath = buildout_url.split('/')[-1]
    with chdir(destination_dir):
        urlretrieve(buildout_url, buildout_filepath)

def download_distribute(destination_dir):
    from urllib import urlretrieve
    from infi.pypi_manager import PyPI
    buildout_url = PyPI().get_latest_source_distribution_url("distribute")
    buildout_filepath = buildout_url.split('/')[-1]
    with chdir(destination_dir):
        urlretrieve(buildout_url, buildout_filepath)
        urlretrieve("http://python-distribute.org/distribute_setup.py", "distribute_setup.py")

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
    get_version = lambda dist: dist.version
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
