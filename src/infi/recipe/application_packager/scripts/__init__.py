from __future__ import print_function
__import__("pkg_resources").declare_namespace(__name__)

from sys import argv, version_info
import time
import os

if version_info > (3, 0):
    _input = input
else:
    _input = raw_input


INSTALLDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), #scripts
                                          os.path.pardir, #application_packager
                                          os.path.pardir, #recipe
                                          os.path.pardir, #infi
                                          os.path.pardir, #src
                                          os.path.pardir))

from .refactoring import before

def packager_hello(argv=argv):
    before()
    print('hello world')

def _write_file(name):
    with open(os.path.join(INSTALLDIR, name), 'w') as fd:
        fd.write(' ')

def post_install(argv=argv):
    before()
    _write_file('post_install')

def pre_uninstall(argv=argv):
    _write_file(os.path.join(INSTALLDIR, os.path.pardir, 'pre_uninstall'))

def packager_sample(argv=argv):
    before()
    _input('sample, hit enter to exit')

def packager_sleep(argv=argv):
    before()
    t0 = time.time()
    timeout = int(argv[-1])
    try:
        time.sleep(timeout)
    except KeyboardInterrupt:  # windows installer does this
        timeout = abs(timeout - (time.time() - t0))
        time.sleep(timeout)
