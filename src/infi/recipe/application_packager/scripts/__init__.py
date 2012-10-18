from __future__ import print_function
__import__("pkg_resources").declare_namespace(__name__)

from sys import argv
import os

INSTALLDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), #scripts
                                          os.path.pardir, #application_packager
                                          os.path.pardir, #recipe
                                          os.path.pardir, #infi
                                          os.path.pardir, #src
                                          os.path.pardir))

def main(argv=argv):
    print('hello world')

def _write_file(name):
    with open(os.path.join(INSTALLDIR, name), 'w') as fd:
        fd.write(' ')

def post_install(argv=argv):
    _write_file('post_install')

def pre_uninstall(argv=argv):
    _write_file(os.path.join(INSTALLDIR, os.path.pardir, 'pre_uninstall'))

def sample(argv=argv):
    raw_input('sample, hit enter to exit')
