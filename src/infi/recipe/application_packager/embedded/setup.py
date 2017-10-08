import setuptools
import subprocess
import distutils.core
import json
import mock
import glob
import os


class SourceFileMissing(Exception):
    pass


def _iter_files(dirname, suffix=None):
    for dirpath, dirnames, filenames in os.walk(dirname):
        for basename in filenames:
            if not suffix or basename.endswith(suffix):
                yield os.path.join(dirpath, basename)


def scan_for_python_files(dirpath, prefix=None):
    python_files = []
    prefix = (prefix.strip('.') + '.') if prefix and os.path.exists(os.path.join(dirpath, '__init__.py')) else ''
    for py in _iter_files(dirpath, '.py'):
        name = prefix + os.path.relpath(py, os.path.abspath(dirpath)).replace(".py", '').replace("__init__", '')
        name = name.replace(os.path.sep, '.').strip('.')
        if ' ' in name:
            continue
        python_files.append(dict(package="__init__.py" in py, source=os.path.abspath(py), name=name))
    return python_files


def _is_cython_importable():
    try:
        import Cython
    except ImportError:
        return False
    return True


def _generate_cython(filepath):
    before = glob.glob(filepath.replace('.pyx', '.*'))
    subprocess.check_call([os.environ['PYTHON_EXECUTABLE'], os.environ['PYTHON_SCRIPT'], '-m', 'cython', filepath])
    after = glob.glob(filepath.replace('.pyx', '.*'))
    return (set(after)-set(before)).pop()


def _generate_cython_if_necssary(filepath):
    if filepath.endswith('.pyx'):
        return _generate_cython(filepath)
    if not os.path.exists(os.path.abspath(filepath)):
        if filepath.endswith('.c') or filepath.endswith('.cpp'):
            if _is_cython_importable():
                return _generate_cython(filepath.rsplit('.', 1)[0] + '.pyx')
            else:
                raise SourceFileMissing()
    return filepath


def _setup(package_dir={}, packages={}, ext_modules=[], py_modules=[], **kwargs):
    if kwargs.get('pbr'):
        config = setuptools.config.read_configuration("setup.cfg")
        packages = [config['metadata']['name']]
    python_files, c_extensions = [], []
    previous_package = '*'
    for package in packages:
        if previous_package in package:
            break
        dirpath = os.path.abspath(package_dir.get('', package))
        python_files.extend(scan_for_python_files(dirpath, package))
        previous_package = package
    for ext_module in ext_modules:
        env = dict(CPPDEFINES=["{}={}".format(item[0], item[1]) for item in ext_module.define_macros],
                   CPPPATH=[os.path.abspath(item) for item in ext_module.include_dirs],
                   LINKFLAGS=ext_module.extra_link_args,
                   CCFLAGS=[repr(i) for i in ext_module.extra_compile_args])
        absolute_sources = [os.path.abspath(source) for source in ext_module.sources]
        absolute_roots = list(set([os.path.abspath(os.path.dirname(source)) for source in ext_module.sources]))
        try:
            fixed_sources = [_generate_cython_if_necssary(item) for item in absolute_sources]
        except SourceFileMissing:
            continue
        c_extensions.append(dict(name=ext_module.name,
                                 sources=list(fixed_sources),
                                 roots=absolute_roots,
                                 depends=ext_module.depends, env=env))
    for py_module in py_modules:
        python_files.append(dict(package=False, source=os.path.abspath(py_module + '.py'), name=py_module))
    with open("_embed_recipe.json", 'w') as fd:
        fd.write(json.dumps(dict(python_files=python_files, c_extensions=c_extensions), indent=4))
    return mock.MagicMock()


def main():
    with mock.patch.object(setuptools, "setup", new=_setup):
        with mock.patch.object(distutils.core, "setup", new=_setup):
            with open('setup.py') as fd:
                exec(fd.read())


if __name__ == "__main__":
    # calling main breaks the global SETUP_INFO in the setup.in template we use
    with mock.patch.object(setuptools, "setup", new=_setup):
        with mock.patch.object(distutils.core, "setup", new=_setup):
            with open('setup.py') as fd:
                exec(fd.read())
