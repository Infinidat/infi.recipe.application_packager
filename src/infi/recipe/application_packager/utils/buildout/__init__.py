
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
recipe = infi.recipe.console_scripts
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

def write_buildout_configuration_file_for_production(dependent_scripts, eggs, scripts, require_administrative_privileges):
    from textwrap import dedent
    from ConfigParser import ConfigParser
    with open("buildout.in", 'w') as fd:
        fd.write(dedent(BUILDOUT_IN))
    with open_buildout_configfile("buildout.in", True) as buildout:
        buildout.set("production-scripts", "dependent-scripts", dependent_scripts)
        buildout.set("production-scripts", "eggs", eggs)
        if scripts:
            buildout.set("production-scripts", "scripts", scripts)
        buildout.set("production-scripts" ,"require-administrative-privileges", require_administrative_privileges)