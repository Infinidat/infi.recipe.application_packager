import tarfile
from os import path
from glob import glob
from logging import getLogger
from zc.buildout.download import Download


logger = getLogger(__name__)
DOWNLOAD_BASE = 'ftp://python.infinidat.com/python/sources'


def get_isolated_python_source(buildout, options):
    """:returns: 2-tuple (url, version)"""
    isolated_python_section = options.get("isolated-python-section", "isolated-python")
    if isolated_python_section not in buildout:
        raise RuntimeError("isolated python section {!r} not found".format(isolated_python_section))
    if 'version' not in buildout[isolated_python_section]:
        raise RuntimeError("isolated python version not found")
    download_base = buildout.get(isolated_python_section).get('download-base', DOWNLOAD_BASE)
    python_version = buildout.get(isolated_python_section).get('version').lstrip('v')
    official_python_version = '.'.join(python_version.split('.')[:3])
    url = '/'.join([download_base, 'Python-{}.tgz'.format(official_python_version)])
    return url, official_python_version


def download(buildout, source_url):
    downloader = Download(buildout.get('buildout'))
    logger.info("downloading {}".format(source_url))
    return downloader(source_url)[0]


def extract(filepath, extract_path):
    if glob(path.join(extract_path, 'Python*')):
        logger.info("skipping extracting {}".format(filepath))
        return
    archive = tarfile.open(filepath, 'r:gz')
    logger.info("extracting {}".format(filepath))
    archive.extractall(extract_path)
    archive.close()


def get_python_source(buildout, options):
    source_url, source_version = get_isolated_python_source(buildout, options)
    source_filepath = download(buildout, source_url)
    base_directory = path.join(buildout.get('buildout').get('directory'), 'build')
    extract(source_filepath, base_directory)
    return path.join(base_directory, 'Python-{}'.format(source_version))
