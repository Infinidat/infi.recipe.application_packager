# TODO pystick expects some files, describe here what is expects for reference


from .scons_variables import SCONS_VARIABLE_NAMES
from sysconfig import get_config_var
from pkg_resources import ensure_directory, resource_filename
from platform import system
from json import dumps
from os import path, name as os_name

SCONSCRIPT_TEMPLATE = """env = DefaultEnvironment()
{%- for key, value in sorted(environment_variables.items()) %}
{%- if key.startswith("!") %}
env[{{ repr(key[1:]) }}] = {{ repr(value) }}
{%- else %}
env.Append({{ key }}={{ repr(value) }})
{%- endif %}
{%- endfor %}
"""
DEFINES = dict(HAVE_CURSES=True, HAVE_CURSES_PANEL=True, HAVE_LIBBZ2=True, HAVE_LIBCABINET=True, HAVE_LIBCRYPT=True,
               HAVE_LIBDB=True, HAVE_LIBGDBM=True, HAVE_LIBM=True, HAVE_LIBNSL=True,
               HAVE_LIBRPCRT4=True, HAVE_LIBSQLITE3=True, HAVE_LIBTCL=False, HAVE_LIBTK=False, HAVE_LIBWS2_32=True,
               HAVE_LIBZ=True, HAVE_OPENSSL=True, HAVE_LIBSSL=True, HAVE_LIBCRYPTO=True, HAVE_READLINE=True,
               HAVE_LIBGMP=True, WITH_PYTHON_MODULE_NIS=False, STATIC_PYTHON_MODULES=1)
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


# Extracted from SCons:
def ParseFlags(*flags):
    """
    Parse the set of flags and return a dict with the flags placed
    in the appropriate entry.  The flags are treated as a typical
    set of command-line flags for a GNU-like toolchain and used to
    populate the entries in the dict immediately below.  If one of
    the flag strings begins with a bang (exclamation mark), it is
    assumed to be a command and the rest of the string is executed;
    the result of that evaluation is then added to the dict.
    """
    dict = {
        'ASFLAGS'       : [],
        'CFLAGS'        : [],
        'CCFLAGS'       : [],
        'CXXFLAGS'      : [],
        'CPPDEFINES'    : [],
        'CPPFLAGS'      : [],
        'CPPPATH'       : [],
        'FRAMEWORKPATH' : [],
        'FRAMEWORKS'    : [],
        'LIBPATH'       : [],
        'LIBS'          : [],
        'LINKFLAGS'     : [],
        'RPATH'         : []
    }

    def do_parse(arg):
        # if arg is a sequence, recurse with each element
        if not arg:
            return

        if not isinstance(arg, str):
            for t in arg: do_parse(t)
            return

        # if arg is a command, execute it
        # if arg[0] == '!':
        #     arg = self.backtick(arg[1:])

        # utility function to deal with -D option
        def append_define(name, dict=dict):
            t = name.split('=')
            if len(t) == 1:
                dict['CPPDEFINES'].append(name)
            else:
                dict['CPPDEFINES'].append([t[0], '='.join(t[1:])])

        # Loop through the flags and add them to the appropriate option.
        # This tries to strike a balance between checking for all possible
        # flags and keeping the logic to a finite size, so it doesn't
        # check for some that don't occur often.  It particular, if the
        # flag is not known to occur in a config script and there's a way
        # of passing the flag to the right place (by wrapping it in a -W
        # flag, for example) we don't check for it.  Note that most
        # preprocessor options are not handled, since unhandled options
        # are placed in CCFLAGS, so unless the preprocessor is invoked
        # separately, these flags will still get to the preprocessor.
        # Other options not currently handled:
        #  -iqoutedir      (preprocessor search path)
        #  -u symbol       (linker undefined symbol)
        #  -s              (linker strip files)
        #  -static*        (linker static binding)
        #  -shared*        (linker dynamic binding)
        #  -symbolic       (linker global binding)
        #  -R dir          (deprecated linker rpath)
        # IBM compilers may also accept -qframeworkdir=foo

        import shlex
        params = shlex.split(arg)
        append_next_arg_to = None   # for multi-word args
        for arg in params:
            if append_next_arg_to:
                if append_next_arg_to == 'CPPDEFINES':
                    append_define(arg)
                elif append_next_arg_to == '-include':
                    t = '-include ' + arg
                    dict['CCFLAGS'].append(t)
                elif append_next_arg_to == '-isysroot':
                    t = '-isysroot ' + arg
                    dict['CCFLAGS'].append(t)
                    dict['LINKFLAGS'].append(t)
                elif append_next_arg_to == '-arch':
                    t = '-arch ' + arg
                    dict['CCFLAGS'].append(t)
                    dict['LINKFLAGS'].append(t)
                else:
                    dict[append_next_arg_to].append(arg)
                append_next_arg_to = None
            elif not arg[0] in ['-', '+']:
                dict['LIBS'].append(arg)
            elif arg == '-dylib_file':
                dict['LINKFLAGS'].append(arg)
                append_next_arg_to = 'LINKFLAGS'
            elif arg[:2] == '-L':
                if arg[2:]:
                    dict['LIBPATH'].append(arg[2:])
                else:
                    append_next_arg_to = 'LIBPATH'
            elif arg[:2] == '-l':
                if arg[2:]:
                    dict['LIBS'].append(arg[2:])
                else:
                    append_next_arg_to = 'LIBS'
            elif arg[:2] == '-I':
                if arg[2:]:
                    dict['CPPPATH'].append(arg[2:])
                else:
                    append_next_arg_to = 'CPPPATH'
            elif arg[:4] == '-Wa,':
                dict['ASFLAGS'].append(arg[4:])
                dict['CCFLAGS'].append(arg)
            elif arg[:4] == '-Wl,':
                if arg[:11] == '-Wl,-rpath=':
                    dict['RPATH'].append(arg[11:])
                elif arg[:7] == '-Wl,-R,':
                    dict['RPATH'].append(arg[7:])
                elif arg[:6] == '-Wl,-R':
                    dict['RPATH'].append(arg[6:])
                else:
                    dict['LINKFLAGS'].append(arg)
            elif arg[:4] == '-Wp,':
                dict['CPPFLAGS'].append(arg)
            elif arg[:2] == '-D':
                if arg[2:]:
                    append_define(arg[2:])
                else:
                    append_next_arg_to = 'CPPDEFINES'
            elif arg == '-framework':
                append_next_arg_to = 'FRAMEWORKS'
            elif arg[:14] == '-frameworkdir=':
                dict['FRAMEWORKPATH'].append(arg[14:])
            elif arg[:2] == '-F':
                if arg[2:]:
                    dict['FRAMEWORKPATH'].append(arg[2:])
                else:
                    append_next_arg_to = 'FRAMEWORKPATH'
            elif arg in ['-mno-cygwin',
                         '-pthread',
                         '-openmp',
                         '-fopenmp']:
                dict['CCFLAGS'].append(arg)
                dict['LINKFLAGS'].append(arg)
            elif arg == '-mwindows':
                dict['LINKFLAGS'].append(arg)
            elif arg[:5] == '-std=':
                if arg[5:].find('++') != -1:
                    key = 'CXXFLAGS'
                else:
                    key = 'CFLAGS'
                dict[key].append(arg)
            elif arg[0] == '+':
                dict['CCFLAGS'].append(arg)
                dict['LINKFLAGS'].append(arg)
            elif arg in ['-include', '-isysroot', '-arch']:
                append_next_arg_to = arg
            else:
                dict['CCFLAGS'].append(arg)

    for arg in flags:
        do_parse(arg)
    return dict


def get_config_vars():
    # our relocatable-python passes include dirs in CFLAGS instead of CPPFLAGS
    # this breaks builds of some C extensions (e.g. pymongo)
    # this is a workaround until relocatable-python is fixed
    from sysconfig import get_config_vars as _get_config_vars
    config_vars = _get_config_vars()
    keys = ('CFLAGS', 'CCFLAGS', 'CPPPATH', 'CPPFLAGS', 'LDFLAGS')
    flags_to_extract = [config_vars.get(key, '') for key in keys]
    extracted_config_vars = ParseFlags(*flags_to_extract)
    extracted_config_vars['CFLAGS'] = extracted_config_vars['CCFLAGS']
    config_vars.update((k, v) for k, v in extracted_config_vars.items() if k in keys)
    return config_vars


def _apply_project_specific_on_top_of_platform_defaults(variables, project_specific_flags):
    for key, added_value in project_specific_flags.items():
        if added_value is None:
            continue
        value = variables.get(key)
        if key in ("CC", "CXX", "!CC", "!CXX"):
            variables[key] = added_value
        elif isinstance(value, basestring):
            variables[key] = [value, added_value]
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
    from jinja2 import Template
    from json import dumps
    ensure_directory(pystick_variable_filepath)
    json_reference_dict = _write_json_files(path.dirname(pystick_variable_filepath), python_files, c_extensions)
    variables = dict(scons_variables)
    variables.update(json_reference_dict)
    with open(pystick_variable_filepath, 'w') as fd:
        fd.write(Template(SCONSCRIPT_TEMPLATE).render(repr=repr, sorted=sorted, environment_variables=variables))
    with open(pystick_variable_filepath.replace('.scons', '.json'), 'w') as fd:
        fd.write(dumps(variables))


def locate_vcvars():
    from infi.registry import LocalComputer
    VISUAL_STUDIO_9_REGKEY = "SOFTWARE\\{}Microsoft\\VisualStudio\\9.0".format(r"Wow6432Node\\" if is_64bit() else "")
    try:
        visual_studio_9 = LocalComputer().local_machine[VISUAL_STUDIO_9_REGKEY]
    except KeyError:
        return r"C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin\vcvars64.bat" if is_64bit() else \
               r"C:\Program Files\Microsoft Visual Studio 9.0\VC\bin\vcvars32.bat"
    # installdir = C:\Program Files (x86)\Microsoft Visual Studio 9.0\Common7\IDE\
    # vcvars = C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin\vcvars64.bat
    installdir = visual_studio_9.values_store['InstallDir'].to_python_object()
    basename = 'vcvars64.bat' if is_64bit() else 'vcvars32.bat'
    return path.abspath(path.join(installdir, path.pardir, path.pardir, 'VC', 'bin', basename))


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
    variables = {}
    variables.update(DEFINES)
    variables.update(WINDOWS_DEFINES_UPDATE)
    manifest = resource_filename(__name__, 'Microsoft.VC90.CRT.manifest-{}'.format('x64' if is_64bit() else 'x86'))
    manifest_embedded = "mt.exe -nologo -manifest {} -outputresource:$TARGET;2".format(manifest)
    if is_64bit():
        # variables['!AS'] = '"C:\\Program Files (x86)\\Microsoft Visual Studio 9.0\\VC\\bin\\amd64\\ml64.exe"'
        variables['!AS'] = 'ml64'

    variables.update(
        LIBPATH=[static_libdir],
        LIBS=WINDOWS_NATIVE_LIBS + static_libs,
        CCPDBFLAGS=['/Z7'],
        LINKFLAGS="/RELEASE",
        LINKCOM=manifest_embedded,
    )
    variables['!MSVC_USE_SCRIPT'] = locate_vcvars()
    return variables


def get_scons_variables__linux(static_libdir, static_libs):
    variables = {'!{}'.format(key): value for key, value in get_config_vars().items() if key in SCONS_VARIABLE_NAMES}
    variables.update(DEFINES)
    variables.update({
        "!LIBPATH": [static_libdir],
        "!LIBS": static_libs + ['crypt', 'dl', 'util', 'm', 'rt'],
        "!CC": ' '.join([variables['!CC'], get_config_var('CCSHARED')]),  # provides -fPIC
        "CCFLAGS": ['-g', '-pthread'],
        "CXXFLAGS": ['-g', '-pthread']
        },
    )
    return variables


def get_scons_variables__osx(static_libdir, static_libs):
    variables = {'!{}'.format(key): value for key, value in get_config_vars().items() if key in SCONS_VARIABLE_NAMES}
    variables.update(DEFINES)
    variables.update(OSX_DEFINES_UPDATE)
    variables.update({
        "!LIBPATH": [static_libdir],
        "!LIBS": static_libs + ['iconv', 'dl'],
        "!LINKFLAGS": ' '.join(['-framework CoreFoundation -framework SystemConfiguration -framework IOKit'])
        },
    )
    return variables


def get_scons_variables(static_libdir, options):
    static_libs = get_names_of_static_libraries_for_linking(static_libdir)
    project_specific_flags = dict({
                                  "!CPPPATH": options.get('CPPPATH', None),
                                  "!CPPDEFINES": options.get('CPPDEFINES', None),
                                  "!CPPFLAGS": options.get('CPPFLAGS', None),
                                  "!LINKFLAGS": options.get('LINKFLAGS', None),
                                  "!CFLAGS": options.get('CFLAGS', None),
                                  "!CCFLAGS": options.get('CCFLAGS', None),
                                  "!LIBS": options.get('LIBS', None),
                                  "!CC": options.get('CC', None),
                                  "!CXX": options.get('CXX', None),
                                  "!PATH": options.get('PATH', None),
                                  "!LIBRARY_PATH": options.get('LIBRARY_PATH', None),
                                  "!LD_LIBRARY_PATH": options.get('LD_LIBRARY_PATH', None),
                                  }) if system() != "Windows" else dict()
    if system() == "Linux":
        variables = get_scons_variables__linux(static_libdir, static_libs)
    elif system() == "AIX":
        variables = get_scons_variables__linux(static_libdir, static_libs)
    elif system() == "SunOS":
        variables = get_scons_variables__linux(static_libdir, static_libs)
    elif system() == "Darwin":
        variables = get_scons_variables__osx(static_libdir, static_libs)
    elif system() == "Windows":
        variables = get_scons_variables__windows(static_libdir, static_libs)
    else:
        variables = dict()
    python_include_dir = path.abspath(path.join('parts', 'python', 'include'))
    current_cpppath = variables.get('!CPPPATH', [])
    if python_include_dir not in current_cpppath:
        current_cpppath = [python_include_dir] + current_cpppath
    variables['!CPPPATH'] = current_cpppath
    final_variables = _apply_project_specific_on_top_of_platform_defaults(variables, project_specific_flags)
    return final_variables


def get_names_of_static_libraries_for_linking(static_libdir):
    """
    :returns: a list of names of libraries under static_libdir, sorted as linking-order in the isolated-python build
    """
    names = []
    prefix, suffix = ('', '.lib') if system() == "Windows" else ('lib', '.a')
    for name in STATIC_LIBS:
        if path.exists(path.join(static_libdir, '{}{}{}'.format(prefix, name, suffix))):
            names.append(name)
    return names


def get_sorted_static_libraries(static_libdir):
    """
    :returns: a list of filepaths under static_libdir, sorted as linking-order in the isolated-python build
    """
    files = []
    prefix, suffix = ('', '.lib') if system() == "Windows" else ('lib', '.a')
    for name in STATIC_LIBS:
        filepath = path.join(static_libdir, '{}{}{}'.format(prefix, name, suffix))
        if path.exists(filepath):
            files.append(filepath)
    return files
