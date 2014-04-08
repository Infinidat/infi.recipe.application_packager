# TODO pystick expects some files, describe here what is expects for reference


from .scons_construction_variables import SCONS_VARIABLE_NAMES
from sysconfig import get_config_var, get_config_vars
from pkg_resources import ensure_directory
from platform import system
from json import dumps
from glob import glob
from os import path


DEFINES = dict(HAVE_CURSES=True, HAVE_CURSES_PANEL=True, HAVE_LIBBZ2=True, HAVE_LIBCABINET=True, HAVE_LIBCRYPT=True,
               HAVE_LIBDB=True, HAVE_LIBGDBM=True, HAVE_LIBM=True, HAVE_LIBNSL=True,
               HAVE_LIBRPCRT4=True, HAVE_LIBSQLITE3=True, HAVE_LIBTCL=False, HAVE_LIBTK=False, HAVE_LIBWS32_32=True,
               HAVE_LIBZ=True, HAVE_OPENSSL=True, HAVE_READLINE=True,
               WITH_PYTHON_MODULE_NIS=False, STATIC_PYTHON_MODULES=1)
ISOLATED_PYTHON_LIBS = ['z',
                        'ncurses', 'form', 'panel', # all provided by ncurses
                        'readline', 'history', # all provided by readline
                        'ssl', 'crypto', # all provided by openssl
                        'gpg-error', 'gcrypt', 'tasn1', 'gmp',
                        'nettle', 'hogweed', # providef by nettle
                        'gettext', 'asprintf', 'gettextpo', 'intl', # all provided by gettext
                        'iconv',
                        'gnutls', 'xssl', # all provided by gnutls
                        'bz2', 'sqlite3', 'db',
                        'xml2', 'xslt', 'exslt',
                        'ffi', 'gdbm', 'sasl2',
                        'event',
                        'event_core', 'event_extra', # all provided by libevent
                        'ev', 'zmq',
                        'ldap', 'ldap_r', 'lber', # all oprvided by openldap
                        ]
# osx parts = zlib ncurses readline openssl openssh libgpg-error libgcrypt libtasn1 gmp nettle gettext          libgnutls bzip2 sqlite3 db libxml2 libxslt libffi gdbm cyrus-sasl libevent libev zeromq openldap graphviz python
# std parts = zlib ncurses readline openssl openssh libgpg-error libgcrypt                     gettext libiconv libgnutls bzip2 sqlite3 db libxml2 libxslt libffi gdbm cyrus-sasl libevent libev zeromq openldap graphviz python

STATIC_LIBS = reversed(ISOLATED_PYTHON_LIBS)


def _write_json_files(base_directory, python_files, c_extensions):
    python_modules_file = path.join(base_directory, 'python_files.json')
    c_modules_file = path.join(base_directory, 'c_modules.json')
    with open(python_modules_file, 'w') as fd:
        fd.write(dumps(python_files, indent=4))
    with open(c_modules_file, 'w') as fd:
        fd.write(dumps(c_extensions, indent=4))
    return dict(EXTERNAL_PY_MODULES_FILE=python_modules_file, EXTERNAL_C_MODULES_FILE=c_modules_file)


def write_pystick_variable_file(pystick_variable_filepath, python_files, c_extensions, construction_variables):
    from pprint import pformat
    ensure_directory(pystick_variable_filepath)
    json_reference_dict = _write_json_files(path.dirname(pystick_variable_filepath), python_files, c_extensions)
    variables = dict(construction_variables)
    variables.update(json_reference_dict)
    with open(pystick_variable_filepath, 'w') as fd:
        fd.write("env = DefaultEnvironment(\n**{}\n)\n".format(pformat(variables, indent=4)))


def get_construction_variables__windows(static_libdir, options):
    # 32bit
    # APPVER = 5.02
    # CPU = i386
    # TARGETOS = WINNT
    # FrameworkVersion = v2.0.50727
    # OS = Windows_NT
    # RegKeyPath = HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\SxS\VC7
    # VSRegKeyPath = HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\SxS\VS7
    # SystemDrive = C:
    # WinDir = ${:SystemDrive}\WINDOWS
    # ProgramFiles = ${:SystemDrive}\Program Files
    # ORIGINALPATH = ${:WinDir}\system32;${:WinDir};${:WinDir}\System32\Wbem;${:ProgramFiles}\Git\cmd;${:ProgramFiles}\Git\bin;C:\Python27

    # FrameworkDir = ${:WinDir}\Microsoft.NET\Framework
    # FxTools = ${:FrameworkDir}\v3.5;${:FrameworkDir}\v2.0.50727
    # WindowsSdkDir = ${:ProgramFiles}\Microsoft SDKs\Windows\v7.0
    # VSINSTALLDIR = ${:ProgramFiles}\Microsoft Visual Studio 9.0
    # VCRoot = ${:VSINSTALLDIR}\VC
    # VCINSTALLDIR = ${:VCRoot}
    # VC90CRT = ${:VCRoot}\redist\x86\Microsoft.VC90.CRT
    # INCLUDE = ${:VCRoot}\Include;${:WindowsSdkDir}\Include;${:WindowsSdkDir}\Include\gl;${:VCRoot}\ATLMFC\INCLUDE;
    # MSSdk = ${:WindowsSdkDir}
    # NODEBUG = 1
    # SdkSetupDir = ${:WindowsSdkDir}\Setup
    # SdkTools = ${:WindowsSdkDir}\Bin
    # DevEnvDir = ${:VSINSTALLDIR}\Common7\IDE
    # INCLUDE = ${:VCRoot}\ATLMFC\INCLUDE;${:VCRoot}\INCLUDE;${:WindowsSdkDir}\include;${:PREFIX}\include
    # ATLMFC_LIB = ${:VCRoot}\ATLMFC\LIB
    # VSLIB = ${:VCRoot}\LIB
    # SDKLIB = ${:WindowsSdkDir}\lib
    # SDKBIN = ${:WindowsSdkDir}\bin
    # LIB = ${:ATLMFC_LIB};${:VSLIB};${:SDKLIB};${:PREFIX}\lib
    # LIBPATH = ${:FrameworkDir};${:FrameworkDir}\v2.0.50727;${:ATLMFC_LIB};${:VSLIB}
    # Recipe = hexagonit.recipe.cmmi
    # VSBIN = ${:VCRoot}\BIN
    # PosixHomeDir=${:SystemDrive}\Cygwin\home\Administrator
    # GitDir = ${:PosixHomeDir}\git
    # GitBinDir = ${:GitDir}\bin
    # PythonDir = ${:PosixHomeDir}\python\bin
    # PythonBinDir = ${:PythonDir}\bin
    # PATH = ${:DevEnvDir};${:VSBIN};${:VSINSTALLDIR}\Common7\Tools;${:VSINSTALLDIR}\Common7\Tools\bin;${:FrameworkDir};${:FrameworkDir}\Microsoft .NET Framework 3.5 (Pre-Release Version);${:FrameworkDir}\v2.0.50727;${:VCRoot}\VCPackages;${:SDKBIN};${:WinDir}\system32;${:WinDir};${:WinDir}\System32\Wbem;${:GitDir}\cmd;${:GitBinDir};${:PythonBinDir}
    # PREFIX = ${options:prefix}
    # IIPREFIX = ${options:prefix}
    # PerlExe = ${:SystemDrive}\Perl\bin\perl.exe

    # 64bit
    # FrameworkDir = ${:WinDir}\Microsoft.NET\Framework64
    # VSINSTALLDIR = ${:ProgramFiles64}\Microsoft Visual Studio 9.0
    # ProgramFiles64 = ${:SystemDrive}\Program Files (x86)
    # VSBIN = ${:VCRoot}\BIN\amd64
    # ATLMFC_LIB = ${:VCRoot}\ATLMFC\LIB\amd64
    # VSLIB = ${:VCRoot}\LIB\amd64
    # VC90CRT = ${:VCRoot}\redist\amd64\Microsoft.VC90.CRT
    # SDKLIB = ${:WindowsSdkDir}\lib\x64
    # SDKLIB32 = ${:WindowsSdkDir}\lib
    # SDKBIN = ${:WindowsSdkDir}\bin\x64
    # PerlExe = ${:SystemDrive}\Perl64\bin\perl.exe
    pass


def get_construction_variables__linux(static_libdir, static_libs, project_specific_flags):
    variables = {key: value for key, value in get_config_vars().items() if key in SCONS_VARIABLE_NAMES}
    variables.update(DEFINES)
    variables.update(
        LIBPATH=[static_libdir],
        LIBS=static_libs + ['pthread', 'crypt', 'dl', 'util', 'm'],
        CC=' '.join([variables['CC'],
                     get_config_var('CCSHARED') # provides -fPIC
                    ]),
    )
    return variables


def get_construction_variables__osx(static_libdir, static_libs, project_specific_flags):
    variables = {key: value for key, value in get_config_vars().items() if key in SCONS_VARIABLE_NAMES}
    variables.update(DEFINES)
    variables.update(
        LIBPATH=[static_libdir],
        LIBS=static_libs + ['iconv', 'dl'],
        LINKFLAGS=' '.join(['-framework CoreFoundation -framework SystemConfiguration',
                           ]),
    )
    return variables


def get_construction_variables(static_libdir, options):
    static_libs = get_names_of_static_libraries_for_linking(static_libdir)
    project_specific_flags = ' {}'.format(options.get('xflags', ''))

    # if system() == "Windows":
        # return get_construction_variables__windows()
    if system() == "Linux":
        return get_construction_variables__linux(static_libdir, static_libs, project_specific_flags)
    if system() == "Darwin":
        return get_construction_variables__osx(static_libdir, static_libs, project_specific_flags)


def get_names_of_static_libraries_for_linking(static_libdir):
    names = []
    prefix, suffix  = ('', '.lib') if system() == "Windows" else ('lib', '.a')
    for name in STATIC_LIBS:
        if path.exists(path.join(static_libdir, '{}{}{}'.format(prefix, name, suffix))):
            names.append(name)
    return names


def get_static_libraries(static_libdir):
    return [item for item in glob(path.join(static_libdir, '*')) if
            'python2.7' not in item and not item.endswith('.rsp')]


def get_sorted_static_libraries(static_libdir):
    files = []
    prefix, suffix  = ('', '.lib') if system() == "Windows" else ('lib', '.a')
    for name in STATIC_LIBS:
        filepath = path.join(static_libdir, '{}{}{}'.format(prefix, name, suffix))
        if path.exists(filepath):
            files.append(filepath)
    return files
