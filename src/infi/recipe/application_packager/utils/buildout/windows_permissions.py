"""Standalone MSI ACL repair for installed public Python dependencies only."""

import ctypes
from ctypes import wintypes
import logging
import os
import stat
import subprocess
import sys


logger = logging.getLogger(__name__)
_REPARSE_POINT = 0x400
_CREATE_NO_WINDOW = 0x08000000


def _icacls_executable():
    # Do not search PATH or trust a caller-controlled SystemRoot environment.
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    get_directory = kernel.GetSystemDirectoryW
    get_directory.argtypes = [wintypes.LPWSTR, wintypes.UINT]
    get_directory.restype = wintypes.UINT
    buffer = ctypes.create_unicode_buffer(32768)
    length = get_directory(buffer, len(buffer))
    if not length:
        raise ctypes.WinError()
    if length >= len(buffer):
        raise RuntimeError("Windows system directory exceeds the path buffer")
    return os.path.join(buffer.value, "icacls.exe")


def _validate_path(path, info, directory=False):
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & _REPARSE_POINT:
        raise RuntimeError("Refusing to repair dependency ACLs through a link or reparse point: {}".format(path))
    if directory and not stat.S_ISDIR(info.st_mode):
        raise RuntimeError("Dependency ACL repair requires a directory: {}".format(path))
    if not stat.S_ISDIR(info.st_mode):
        if not stat.S_ISREG(info.st_mode) or info.st_nlink > 1:
            raise RuntimeError("Refusing to repair dependency ACLs on a special or hard-linked file: {}".format(path))


def _validate_egg_tree(eggs):
    from pathlib import Path
    # Check the whole path before invoking a recursive ACL tool. Never follow
    # junctions/symlinks or change a hard-linked object outside the eggs tree.
    for parent in reversed(eggs.parents):
        _validate_path(parent, parent.lstat(), directory=True)
    _validate_path(eggs, eggs.lstat(), directory=True)
    pending = [eggs]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                # Windows DirEntry.stat() reports st_nlink=0; use a fresh
                # lstat so hard links are detected without following links.
                info = os.lstat(entry.path)
                _validate_path(entry.path, info)
                if stat.S_ISDIR(info.st_mode):
                    pending.append(Path(entry.path))


def restore_egg_permissions(project_root):
    """Restore inherited installation ACLs, never credentials/log/config ACLs.

    Buildout stages dependencies below mkdtemp(mode=0o700). On patched Python
    3.8+ Windows builds this ACL is protected and retained when renamed into
    eggs, instead of inheriting the installation directory's normal ACL.
    Run from the system-context MSI action after buildout, before post_install.
    """
    if sys.platform != "win32" or sys.version_info < (3, 8):
        return  # Legacy Python builds predate the mkdir(0o700) ACL change.
    from pathlib import Path
    eggs = Path(project_root).absolute() / "eggs"
    try:
        eggs.lstat()
    except FileNotFoundError:
        return  # Development/standalone installations may not have eggs.
    executable = _icacls_executable()
    for operation in ("/inheritance:e", "/reset"):
        _validate_egg_tree(eggs)
        logger.info("Restoring installed Python dependency ACLs: %s %s", eggs, operation)
        try:
            subprocess.run(
                [executable, str(eggs), operation, "/T", "/Q", "/L"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, errors="replace", creationflags=_CREATE_NO_WINDOW,
            )
        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                "Could not restore installed Python dependency ACLs at {}: {}".format(
                    eggs, (error.stdout or "icacls exit code {}".format(error.returncode)).strip()
                )
            )


def main():
    # MSI copies this file to INSTALLDIR. Do not depend on cwd or installed eggs
    # to locate the installation or import application/packager code.
    restore_egg_permissions(os.path.dirname(os.path.abspath(__file__)))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
