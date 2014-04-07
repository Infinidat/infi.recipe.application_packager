# TODO pystick expects some files, describe here what is expects for reference


from sysconfig import get_config_var, get_config_vars
from pkg_resources import ensure_directory
from platform import system
from json import dumps
from glob import glob
from os import path


DEFINES = ["HAVE_CURSES=1", "HAVE_CURSES_PANEL=1", "HAVE_LIBBZ2=1", "HAVE_LIBCABINET=1", "HAVE_LIBCRYPT=1",
           "HAVE_LIBDB=1", "HAVE_LIBGDBM=1", "HAVE_LIBM=1", "HAVE_LIBNSL=1",
           "HAVE_LIBRPCRT4=1", "HAVE_LIBSQLITE3=1", "HAVE_LIBTCL=0", "HAVE_LIBTK=0", "HAVE_LIBWS32_32=1",
           "HAVE_LIBZ=1", "HAVE_OPENSSL=1", "HAVE_READLINE=1",
           "WITH_PYTHON_MODULE_NIS=0"]
STATIC_LIBS = ['zmq', 'ev', 'event', 'ffi', 'gdmb', 'xslt', 'xml2', 'db,' 'sqlite3', 'gettext', ',bz2',
               'panel', 'form', 'menu', 'iconv', 'gnutls', 'readline', 'ncurses', 'z']


def _write_json_files(base_directory, python_files, c_extensions):
    python_modules_file = path.join(base_directory, 'python_files.json')
    c_modules_file = path.join(base_directory, 'c_modules.json')
    with open(python_modules_file, 'w') as fd:
        fd.write(dumps(python_files))
    with open(c_modules_file, 'w') as fd:
        fd.write(dumps(c_extensions, indent=4))
    return dict(EXTERNAL_PY_MODULES_FILE=python_modules_file, EXTERNAL_C_MODULES_FILE=c_modules_file)


def write_pystick_variable_file(pystick_variable_filepath, python_files, c_extensions, xflags, precompiled_static_libs):
    ensure_directory(pystick_variable_filepath)
    json_reference_dict = _write_json_files(path.dirname(pystick_variable_filepath), python_files, c_extensions)
    with open(pystick_variable_filepath, 'w') as fd:
        fd.write("STATIC_PYTHON_MODULES=1\n")
        fd.write("PRECOMPILED_STATIC_LIBS={!r}\n".format(precompiled_static_libs))
        fd.write("XFLAGS={!r}\n".format(xflags))
        for key, value in json_reference_dict.items():
            fd.write("{}={!r}\n".format(key, value))
        for item in DEFINES:
            fd.write("{}\n".format(item))


def get_xflags(static_libdir, options):
    static_libs = get_names_from_sorted_static_libdir(static_libdir)
    if 'ncurses' in static_libs:
        static_libs.remove('ncurses')
        static_libs.append('ncurses')
    static_libs_formatted = ' '.join(['-l{}'.format(item) for item in static_libs])
    xflags = ' '.join([get_config_var('CFLAGS') or '',
                       get_config_var('CCSHARED') or '',
                       '-L{}'.format(static_libdir), get_config_var('LDFLAGS') or '',
                       get_config_var("SHLIBS") or '', get_config_var("SYSLIBS") or '',
                       static_libs_formatted])
    system_specific_flags = dict(Linux=' -lpthread -lcrypt', Darwin=' -framework SystemConfiguration')
    project_specific_flags = ' {}'.format(options.get('xflags', ''))
    xflags += system_specific_flags.get(system(), '') + project_specific_flags
    return xflags


def get_static_libraries(static_libdir):
    return [item for item in glob(path.join(static_libdir, '*')) if
            'python2.7' not in item and not item.endswith('.rsp')]


def get_sorted_static_libraries(static_libdir):
    static_libs = get_static_libraries(static_libdir)
    def _index(lib):
        items = [name for name in STATIC_LIBS if name in lib] or [None]
        return STATIC_LIBS.index(items[0]) if items and items[0] in STATIC_LIBS else None
    sorted_static_libs = sorted(static_libs, key=_index)
    return sorted_static_libs


def get_names_from_static_libdir(static_libdir):
    return [path.basename(item.rsplit('.', 1)[0])[3:] for item in get_static_libraries(static_libdir)]


def get_names_from_sorted_static_libdir(static_libdir):
    return [path.basename(item.rsplit('.', 1)[0])[3:] for item in get_sorted_static_libraries(static_libdir)]
