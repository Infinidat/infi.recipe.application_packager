# TODO pystick expects some files, describe here what is expects for reference


from .scons_variables import SCONS_VARIABLE_NAMES
from sysconfig import get_config_var, get_config_vars
from pkg_resources import ensure_directory, resource_filename
from platform import system
from json import dumps
from glob import glob
from os import path, name as os_name

DEFINES = dict(HAVE_CURSES=True, HAVE_CURSES_PANEL=True, HAVE_LIBBZ2=True, HAVE_LIBCABINET=True, HAVE_LIBCRYPT=True,
               HAVE_LIBDB=True, HAVE_LIBGDBM=True, HAVE_LIBM=True, HAVE_LIBNSL=True,
               HAVE_LIBRPCRT4=True, HAVE_LIBSQLITE3=True, HAVE_LIBTCL=False, HAVE_LIBTK=False, HAVE_LIBWS2_32=True,
               HAVE_LIBZ=True, HAVE_OPENSSL=True, HAVE_LIBSSL=True, HAVE_LIBCRYPTO=True, HAVE_READLINE=True,
               WITH_PYTHON_MODULE_NIS=False, STATIC_PYTHON_MODULES=1)
WINDOWS_DEFINES_UPDATE = dict(HAVE_CURSES=False, HAVE_CURSES_PANEL=False, HAVE_LIBGDBM=False, HAVE_LIBNDBM=False,
                              HAVE_LIBDB=False, HAVE_READLINE=False, HAVE_LIBCRYPT=False)
OSX_DEFINES_UPDATE = dict(HAVE_READLINE=False)
WINDOWS_NATIVE_LIBS = ['shell32', 'user32', 'advapi32', 'ole32', 'oleaut32', 'gdi32', 'ws2_32']
ISOLATED_PYTHON_LIBS = ['z',
                        'ncurses', 'form', 'panel', # all provided by ncurses
                        'readline', 'history', # all provided by readline
                        'crypto', 'ssl', # all provided by openssl
                        'gpg-error', 'gcrypt', 'tasn1', 'gmp',
                        'nettle', 'hogweed', # providef by nettle
                        'asprintf', 'gettextpo', 'intl', # all provided by gettext
                        'iconv',
                        'gnutls', 'gnutls-extra', 'gnutlsxx', 'gnutls-xssl', # all provided by gnutls
                        'bz2', 'sqlite3', 'db',
                        'xml2', 'xslt', 'exslt',
                        'ffi', 'gdbm', 'sasl2',
                        'event', # contains core and extra
                        'ev', 'zmq',
                        'ldap', 'ldap_r', 'lber', # all oprvided by openldap
                        ]
WINDWS_ISOLATED_PYTHON_LIBS = ['zlib', 'libdb51',
                               'ssleay32', 'libeay32', # all provided by openssl
                               'asprintf', 'intl', # all provided by gettext
                               'iconv', 'charset',
                               'libbz2',
                               'sqlite3ts', 'tcl85ts', 'tk85ts'  # all required by sqlite3
                               'libxml2_a', 'libxslt_a', 'libexslt_a',
                               'libevent', # contains libevent_core and libevent_extras
                               ]
# osx parts = zlib ncurses readline openssl openssh libgpg-error libgcrypt libtasn1 gmp nettle gettext          libgnutls bzip2 sqlite3 db libxml2 libxslt libffi gdbm cyrus-sasl libevent libev zeromq openldap graphviz python
# std parts = zlib ncurses readline openssl openssh libgpg-error libgcrypt                     gettext libiconv libgnutls bzip2 sqlite3 db libxml2 libxslt libffi gdbm cyrus-sasl libevent libev zeromq openldap graphviz python

STATIC_LIBS = list(reversed(WINDWS_ISOLATED_PYTHON_LIBS if os_name == 'nt' else ISOLATED_PYTHON_LIBS))


def _write_json_files(base_directory, python_files, c_extensions):
    python_modules_file = path.join(base_directory, 'python_files.json')
    c_modules_file = path.join(base_directory, 'c_modules.json')
    with open(python_modules_file, 'w') as fd:
        fd.write(dumps(python_files, indent=4))
    with open(c_modules_file, 'w') as fd:
        fd.write(dumps(c_extensions, indent=4))
    return dict(EXTERNAL_PY_MODULES_FILE=python_modules_file, EXTERNAL_C_MODULES_FILE=c_modules_file)


def _apply_project_specific_on_top_of_platform_defaults(variables, project_specific_flags):
    for key, added_value in project_specific_flags.items():
        if added_value is None:
            continue
        value = variables.get(key)
        if key in ("CC", "CXX",):
            variables[key] = added_value
        elif isinstance(value, basestring):
            variables[key] = " ".join([value, added_value])
        elif isinstance(value, list):
            variables[key].append(added_value)
        elif isinstance(value, tuple):
            variables[key] += variables[key] + tuple(added_value, )
        else:
            variables[key] = added_value
    return variables


def is_64bit():
    from sys import maxsize
    return maxsize > 2 ** 32


def write_pystick_variable_file(pystick_variable_filepath, python_files, c_extensions, scons_variables):
    from pprint import pformat
    ensure_directory(pystick_variable_filepath)
    json_reference_dict = _write_json_files(path.dirname(pystick_variable_filepath), python_files, c_extensions)
    variables = dict(scons_variables)
    variables.update(json_reference_dict)
    manifest = resource_filename(__name__, 'Microsoft.VC90.CRT.manifest-{}'.format('x64' if is_64bit() else 'x86'))
    manifest_embedded = "mt.exe -nologo -manifest {} -outputresource:$TARGET;2".format(manifest)

    with open(pystick_variable_filepath, 'w') as fd:
        fd.write("env = DefaultEnvironment(\n**{}\n)\n{}\n".format(pformat(variables, indent=4),
                                                                   "LINKCOM=[env['LINKCOM'], {!r}]".format(manifest_embedded)
                                                                   if os_name == 'nt' else ''))


def get_scons_variables__windows(static_libdir, static_libs):
    # SCons attempts to locate the Visual Studio 'vcvars' batch file from the registry
    # We had some problems with this on 64bit hosts with Visual Studio 2008:
    # * SCons wants to link the 64bit binaries with 'ml' and not 'ml64'
    # * We run SCons over Cygwin OpenSSH, and under Cygwin, SCons doesn't locate the batch file
    #   This has something to do with the registry redirection for 32bit processes, but we didn't investigate further
    # So what we did is running SCons over Remote Desktop on hosts with Visual Studio installed in the default paths
    # and copied the generated environemt from SCons into this recipe
    # So if you have Visual Studio installed into the default location(s), you'll be fine
    # If we'll need to support more environments, we'll give the user control to choose:
    # * Use the default SCons lookup behaviour
    # * Define in the recipe the path for 'vcvars'
    from . import win32, win64
    environment_variables = win64.env if is_64bit() else win32.env
    variables = {key: value for key, value in environment_variables.items() if key in SCONS_VARIABLE_NAMES}
    variables.update(DEFINES)
    variables.update(WINDOWS_DEFINES_UPDATE)
    variables.update(
        MSVC_USE_SCRIPT=False,
        LIBPATH=[static_libdir],
        LIBS=WINDOWS_NATIVE_LIBS + static_libs,
        CPPFLAGS='/I{}'.format(path.abspath(path.join('parts', 'python', 'include'))),
    )
    return variables


def get_scons_variables__linux(static_libdir, static_libs):
    variables = {key: value for key, value in get_config_vars().items() if key in SCONS_VARIABLE_NAMES}
    variables.update(DEFINES)
    variables.update(
        CPPFLAGS='-I{}'.format(path.abspath(path.join('parts', 'python', 'include'))),
        LIBPATH=[static_libdir],
        LIBS=static_libs + ['pthread', 'crypt', 'dl', 'util', 'm'],
        CC=' '.join([variables['CC'],
                     get_config_var('CCSHARED') # provides -fPIC
                    ]),
    )
    return variables


def get_scons_variables__osx(static_libdir, static_libs):
    variables = {key: value for key, value in get_config_vars().items() if key in SCONS_VARIABLE_NAMES}
    variables.update(DEFINES)
    variables.update(OSX_DEFINES_UPDATE)
    variables.update(
        CPPFLAGS='-I{}'.format(path.abspath(path.join('parts', 'python', 'include'))),
        LIBPATH=[static_libdir],
        LIBS=static_libs + ['iconv', 'dl'],
        LINKFLAGS=' '.join(['-framework CoreFoundation -framework SystemConfiguration',
                           ]),
    )
    return variables


def get_scons_variables(static_libdir, options):
    static_libs = get_names_of_static_libraries_for_linking(static_libdir)
    project_specific_flags = dict(
                                  LINKFLAGS=options.get('LINKFLAGS', None),
                                  LIBS=options.get('LIBS', None),
                                  CC=options.get('CC', None),
                                  CXX=options.get('CXX', None),
                                  PATH=options.get('PATH', None),
                                  LIBRARY_PATH=options.get('LIBRARY_PATH', None),
                                  LD_LIBRARY_PATH=options.get('LD_LIBRARY_PATH', None),
                                  ) if system() != "Windows" else dict()
    if system() == "Linux":
        variables = get_scons_variables__linux(static_libdir, static_libs)
    if system() == "Darwin":
        variables = get_scons_variables__osx(static_libdir, static_libs)
    elif system() == "Windows":
        variables = get_scons_variables__windows(static_libdir, static_libs)

    final_variables = _apply_project_specific_on_top_of_platform_defaults(variables, project_specific_flags)
    return final_variables


def get_names_of_static_libraries_for_linking(static_libdir):
    """
    :returns: a list of names of libraries under static_libdir, sorted as linking-order in the isolated-python build
    """
    names = []
    prefix, suffix  = ('', '.lib') if system() == "Windows" else ('lib', '.a')
    for name in STATIC_LIBS:
        if path.exists(path.join(static_libdir, '{}{}{}'.format(prefix, name, suffix))):
            names.append(name)
    return names


def get_sorted_static_libraries(static_libdir):
    """
    :returns: a list of filepaths under static_libdir, sorted as linking-order in the isolated-python build
    """
    files = []
    prefix, suffix  = ('', '.lib') if system() == "Windows" else ('lib', '.a')
    for name in STATIC_LIBS:
        filepath = path.join(static_libdir, '{}{}{}'.format(prefix, name, suffix))
        if path.exists(filepath):
            files.append(filepath)
    return files
