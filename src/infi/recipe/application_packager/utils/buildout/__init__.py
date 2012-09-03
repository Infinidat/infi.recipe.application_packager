
from contextlib import contextmanager
from logging import getLogger

logger = getLogger(__name__)

BUILDOUT_IN = """
[buildout]
include-site-packages = true
install-from-cache = true
relative-paths = false
unzip = true
newest = true
download-cache = .cache
develop = .
parts = production-scripts

[production-scripts]
dependent-scripts = false
recipe = infi.recipe.console_scripts
eggs = {}
"""

@contextmanager
def open_buildout_configfile(filepath="buildout.cfg", write_on_exit=False):
    from ConfigParser import ConfigParser
    parser = ConfigParser()
    parser.read(filepath)
    try:
        yield parser
    finally:
        if not write_on_exit:
            return
        with open(filepath, 'w') as fd:
            parser.write(fd)

def write_buildout_configuration_file_for_production(python_package_name):
    from textwrap import dedent
    with open("buildout.in", 'w') as fd:
        fd.write(dedent(BUILDOUT_IN).format(python_package_name))
