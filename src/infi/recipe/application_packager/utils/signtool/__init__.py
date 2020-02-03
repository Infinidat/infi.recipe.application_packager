
from contextlib import contextmanager
from logging import getLogger

logger = getLogger(__name__)

def ZipFile__add(archive):
    from os import path, listdir
    def add(name, arcname=None):
        if path.isfile(name):
            archive.write(name, arcname or name)
        if path.isdir(name):
            for item in listdir(name):
                add(path.join(name, item), path.join(arcname, item))
    return add

@contextmanager
def open_archive(archive_path, mode='r'):
    from tarfile import TarFile
    from zipfile import ZipFile
    use_ZipFile = archive_path.endswith("zip") or archive_path.endswith("egg") or archive_path.endswith("whl")
    open_func = ZipFile if use_ZipFile else TarFile.open
    archive = open_func(archive_path, mode=mode)
    archive.add = ZipFile__add(archive) if use_ZipFile else archive.add
    try:
        yield archive
    finally:
        archive.close()


def rewrite_record_file(archive_path, tempdir):
    from glob import glob
    from os import path, remove
    from distutils.dist import Distribution
    from wheel.wheelfile import WheelFile
    from .. import temporary_directory_context

    [dist_info] = glob(path.join(tempdir, '*.dist-info'))
    record_file = path.join(dist_info, 'RECORD')
    remove(record_file)

    # we pack the wheel file ourselves and not with "wheel" package but
    # we need to use the package to re-create the record file.
    with temporary_directory_context() as tempwhldir:
        wheel_path = path.join(tempwhldir, path.basename(archive_path))
        with WheelFile(wheel_path, 'w') as wf:
            wf.write_files(tempdir)
        # the wheel file creates the record file on close
        with WheelFile(wheel_path, 'r') as wf:
            wf.extract(wf.record_path, tempdir)


class SigntoolError(Exception):
    pass

class Signtool(object):
    def __init__(self, timestamp_url, authenticode_certificate, certificate_password_file, retry_counter=5):
        super(Signtool, self).__init__()
        from os import path
        from platform import python_version

        if python_version() >= '3.8':
            from pathlib import Path
            self.authenticode_certificate = path.abspath(str(Path(authenticode_certificate).expanduser()))
            self.certificate_password_file = path.abspath(str(Path(certificate_password_file).expanduser()))
        else:
            # os.path.expanduser was changes in py 3.8 and no longer uses HOME on Windows
            self.authenticode_certificate = path.abspath(path.expanduser(authenticode_certificate))
            self.certificate_password_file = path.abspath(path.expanduser(certificate_password_file))

        self.timestamp_url = timestamp_url
        self.retry_counter = retry_counter

    def read_password_from_file(self):
        with open(self.certificate_password_file) as fd:
            return fd.readlines()[0].strip()

    def sign_file(self, filepath):
        from pkg_resources import resource_filename
        from infi.winver import Windows
        from ..execute import execute_assert_success
        signtool = resource_filename(__name__, "signtool.exe")
        args = [signtool, 'sign', '/f', self.authenticode_certificate,
                '/t', self.timestamp_url, '/p', self.read_password_from_file(), '/v', filepath]
        if Windows().greater_than("Windows Server 2008"):
            args.insert(-1, '/fd')
            args.insert(-1, 'SHA256')
        retry_counter = self.retry_counter
        while retry_counter:
            if execute_assert_success(args, allowed_return_codes=[0,2]).get_returncode() == 0:
                return
            retry_counter -= 1
        raise SigntoolError("Failed to sign {} after {} times".format(filepath, self.retry_counter))

    def sign_executables_in_archive(self, archive_path):
        from os import listdir, path
        from .. import temporary_directory_context
        write_mode = 'w:gz' if archive_path.endswith('tar.gz') else 'w'
        with temporary_directory_context() as tempdir:
            with open_archive(archive_path) as archive:
                archive.extractall(tempdir)
            self.sign_executables_in_directory(tempdir)
            if archive_path.endswith('.whl'):
                rewrite_record_file(archive_path, tempdir)
            with open_archive(archive_path, write_mode) as archive:
                for item in listdir(tempdir):
                    archive.add(path.join(tempdir, item), item)

    def sign_executables_in_directory(self, tempdir):
        from os import walk, path
        for dirpath, dirnames, filenames in walk(tempdir):
            for filename in [filename for filename in filenames if filename.endswith('exe')]:
                filepath = path.join(dirpath, filename)
                self.sign_file(filepath)
