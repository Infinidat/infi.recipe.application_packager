
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
parts = debug-logging production-scripts production-gui-scripts
prefer-final = false
log-level = DEBUG

[debug-logging]
recipe = infi.recipe.buildout_logging

[production-scripts]
recipe = infi.recipe.console_scripts

[production-gui-scripts]
recipe = infi.recipe.console_scripts:gui_scripts

[close-application]
recipe = infi.recipe.close_application

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

def write_buildout_configuration_file_for_production(dependent_scripts, minimal_packages, eggs, scripts,
                                                     gui_scripts, require_admin, gui_require_admin):
    from textwrap import dedent
    from ConfigParser import ConfigParser
    with open("buildout.in", 'w') as fd:
        fd.write(dedent(BUILDOUT_IN))
    with open_buildout_configfile("buildout.in", True) as buildout:
        buildout.set("production-scripts", "dependent-scripts", dependent_scripts)
        buildout.set("production-scripts", "minimal-packages", minimal_packages)
        buildout.set("production-scripts", "eggs", eggs)
        if scripts:
            buildout.set("production-scripts", "scripts", scripts)
        buildout.set("production-gui-scripts", "dependent-scripts", dependent_scripts)
        buildout.set("production-gui-scripts", "minimal-packages", minimal_packages)
        buildout.set("production-gui-scripts", "eggs", eggs)
        if gui_scripts:
            buildout.set("production-gui-scripts", "scripts", gui_scripts)
        buildout.set("production-scripts" ,"require-administrative-privileges", require_admin)
        buildout.set("production-gui-scripts" ,"require-administrative-privileges", gui_require_admin)
