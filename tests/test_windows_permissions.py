import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, call, patch

from infi.recipe.application_packager.utils.buildout import windows_permissions as windows_install


class WindowsInstallTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve() / "Host Power Tools"
        self.root.mkdir()
        self.eggs = self.root / "eggs"
        self.eggs.mkdir()
        self.egg = self.eggs / "docopt-0.6.2-py3.11.egg"
        self.egg.mkdir()
        self.module = self.egg / "docopt.py"
        self.module.write_text("# public Python dependency\n")
        self.run = Mock()
        self.executable = r"C:\Windows\System32\icacls.exe"
        for patcher in (
            patch.object(windows_install.sys, "platform", "win32"),
            patch.object(windows_install, "_icacls_executable", return_value=self.executable),
            patch.object(windows_install.subprocess, "run", self.run),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_only_the_installed_eggs_tree_is_repaired(self):
        for name in ("conf", "logs", ".infinidat", "ProgramData"):
            (self.root / name).mkdir()
        windows_install.restore_egg_permissions(self.root)
        self.assertEqual(self.run.call_args_list, [
            call(
                [self.executable, str(self.eggs), operation, "/T", "/Q", "/L"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, errors="replace", creationflags=0x08000000,
            )
            for operation in ("/inheritance:e", "/reset")
        ])

    def test_unix_does_not_inspect_or_change_permissions(self):
        with patch.object(windows_install.sys, "platform", "linux"), patch.object(
            windows_install, "_validate_egg_tree"
        ) as validate:
            windows_install.restore_egg_permissions(self.root)
        validate.assert_not_called()
        self.run.assert_not_called()

    def test_legacy_python_does_not_inspect_or_change_permissions(self):
        for version in ((2, 7, 18), (3, 7, 17)):
            with self.subTest(version=version), patch.object(windows_install.sys, "version_info", version), patch.object(
                windows_install, "_validate_egg_tree"
            ) as validate:
                windows_install.restore_egg_permissions(self.root)
            validate.assert_not_called()
        self.run.assert_not_called()

    def test_script_locates_the_installation_from_its_own_path_not_cwd(self):
        with patch.object(windows_install, "__file__", str(self.root / "restore-egg-permissions.py")), patch.object(
            windows_install, "restore_egg_permissions"
        ) as repair:
            self.assertEqual(windows_install.main(), 0)
        repair.assert_called_once_with(str(self.root))

    def test_an_installation_without_eggs_is_unchanged(self):
        empty = self.root / "standalone"
        empty.mkdir()
        windows_install.restore_egg_permissions(empty)
        windows_install._icacls_executable.assert_not_called()
        self.run.assert_not_called()

    def test_an_eggs_file_is_rejected_before_changing_acls(self):
        other_root = self.root / "broken-install"
        other_root.mkdir()
        (other_root / "eggs").write_text("not a directory")
        with self.assertRaisesRegex(RuntimeError, "requires a directory"):
            windows_install.restore_egg_permissions(other_root)
        self.run.assert_not_called()

    def test_symlink_inside_eggs_is_not_followed(self):
        outside = self.root / "private"
        outside.mkdir()
        try:
            (self.egg / "outside").symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest("symlink creation is not permitted: {}".format(error))
        with self.assertRaisesRegex(RuntimeError, "link or reparse point"):
            windows_install.restore_egg_permissions(self.root)
        self.run.assert_not_called()

    def test_a_symlinked_installation_parent_is_not_followed(self):
        link = self.root.parent / "linked-install"
        try:
            link.symlink_to(self.root, target_is_directory=True)
        except OSError as error:
            self.skipTest("symlink creation is not permitted: {}".format(error))
        with self.assertRaisesRegex(RuntimeError, "link or reparse point"):
            windows_install.restore_egg_permissions(link)
        self.run.assert_not_called()

    def test_a_symlinked_eggs_root_is_not_followed(self):
        other_root = self.root / "linked-eggs-install"
        other_root.mkdir()
        try:
            (other_root / "eggs").symlink_to(self.eggs, target_is_directory=True)
        except OSError as error:
            self.skipTest("symlink creation is not permitted: {}".format(error))
        with self.assertRaisesRegex(RuntimeError, "link or reparse point"):
            windows_install.restore_egg_permissions(other_root)
        self.run.assert_not_called()

    def test_a_hard_link_cannot_change_an_outside_objects_acl(self):
        outside = self.root / "private.db"
        outside.write_text("not a dependency")
        os.link(outside, self.egg / "linked.db")
        with self.assertRaisesRegex(RuntimeError, "hard-linked file"):
            windows_install.restore_egg_permissions(self.root)
        self.run.assert_not_called()

    def test_windows_junction_attributes_are_rejected(self):
        info = SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
        with self.assertRaisesRegex(RuntimeError, "reparse point"):
            windows_install._validate_path(self.egg, info, directory=True)

    def test_failure_is_not_silently_ignored(self):
        self.run.side_effect = subprocess.CalledProcessError(5, "icacls", output="Access is denied")
        with self.assertRaisesRegex(RuntimeError, "Access is denied"):
            windows_install.restore_egg_permissions(self.root)
        self.assertEqual(self.run.call_count, 1)

    def test_reset_failure_is_not_silently_ignored(self):
        self.run.side_effect = [None, subprocess.CalledProcessError(5, "icacls")]
        with self.assertRaisesRegex(RuntimeError, "icacls exit code 5"):
            windows_install.restore_egg_permissions(self.root)
        self.assertEqual(self.run.call_count, 2)

    def test_tree_is_revalidated_before_each_acl_operation(self):
        with patch.object(windows_install, "_validate_egg_tree") as validate:
            windows_install.restore_egg_permissions(self.root)
        self.assertEqual(validate.call_args_list, [call(self.eggs), call(self.eggs)])


class SystemExecutableTests(unittest.TestCase):
    def test_system_directory_comes_from_windows_not_the_environment(self):
        def get_directory(buffer, size):
            buffer.value = r"C:\Windows\System32"
            return len(buffer.value)

        kernel = SimpleNamespace(GetSystemDirectoryW=Mock(side_effect=get_directory))
        with patch.object(windows_install.ctypes, "WinDLL", return_value=kernel, create=True) as loader, patch.dict(
            os.environ, {"SystemRoot": r"C:\untrusted", "PATH": r"C:\untrusted"}
        ):
            result = windows_install._icacls_executable()
        loader.assert_called_once_with("kernel32", use_last_error=True)
        self.assertEqual(result, os.path.join(r"C:\Windows\System32", "icacls.exe"))

    @unittest.skipIf(os.name == "nt", "POSIX no-op verifies isolated standalone script execution")
    def test_script_runs_without_site_packages_or_application_imports(self):
        import sys
        result = subprocess.run(
            [sys.executable, "-I", "-S", windows_install.__file__],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


@unittest.skipUnless(os.name == "nt", "Native Windows ACL integration test")
class NativeWindowsInstallTests(unittest.TestCase):
    def setUp(self):
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            self.skipTest("requires an elevated Windows test process")
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.icacls = windows_install._icacls_executable()
        self.powershell = str(Path(self.icacls).parent / "WindowsPowerShell" / "v1.0" / "powershell.exe")
        self._icacls(self.root, "/grant:r", "*S-1-5-32-545:(OI)(CI)(RX)")
        self.eggs = self.root / "eggs"
        self.eggs.mkdir()
        self.egg = self.eggs / "docopt-0.6.2-py3.11.egg"
        self.egg.mkdir(mode=0o700)
        self.module = self.egg / "docopt.py"
        self.module.write_text("# public dependency\n")
        self.private = self.root / "credentials"
        self.private.mkdir(mode=0o700)
        self.pin = self.private / "pin.dpapi"
        self.pin.write_bytes(b"dummy test data, not real credentials")

    def _icacls(self, path, *arguments):
        subprocess.run([self.icacls, str(path), *arguments], check=True, capture_output=True)

    def _acl(self, path):
        literal = str(path).replace("'", "''")
        script = (
            "$acl = Get-Acl -LiteralPath '{}'; "
            "[pscustomobject]@{{ Sddl=$acl.Sddl; Protected=$acl.AreAccessRulesProtected; "
            "Rules=@($acl.Access | ForEach-Object {{ [pscustomobject]@{{ "
            "Sid=$_.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value; "
            "Rights=[int]$_.FileSystemRights; Inherited=$_.IsInherited; Type=[int]$_.AccessControlType "
            "}} }}) }} | ConvertTo-Json -Depth 4 -Compress"
        ).format(literal)
        result = subprocess.run(
            [self.powershell, "-NoProfile", "-NonInteractive", "-Command", script],
            check=True, capture_output=True, text=True,
        )
        return json.loads(result.stdout)

    def test_repair_and_upgrade_preserve_parent_and_private_acls(self):
        parent_before = self._acl(self.root)["Sddl"]
        private_before = self._acl(self.private)["Sddl"]
        pin_before = self._acl(self.pin)["Sddl"]
        # Also reproduces the faulty ACL when testing with older interpreters.
        self._icacls(self.egg, "/inheritance:r")
        self._icacls(
            self.egg, "/grant:r", "*S-1-5-18:(OI)(CI)(F)", "*S-1-5-32-544:(OI)(CI)(F)"
        )
        self._icacls(self.module, "/reset")
        self.assertFalse(any(rule["Sid"] == "S-1-5-32-545" for rule in self._acl(self.module)["Rules"]))

        for _ in range(2):  # A fresh install and an idempotent upgrade repair.
            windows_install.restore_egg_permissions(self.root)
            for path in (self.eggs, self.egg, self.module):
                acl = self._acl(path)
                self.assertFalse(acl["Protected"])
                users = [rule for rule in acl["Rules"] if rule["Sid"] == "S-1-5-32-545" and rule["Type"] == 0]
                self.assertTrue(users)
                for rule in users:
                    self.assertTrue(rule["Inherited"])
                    self.assertEqual(rule["Rights"] & 0x21, 0x21)  # Read/list and execute/traverse.
                    self.assertFalse(rule["Rights"] & 0x500D0156)  # No write/delete/ACL/owner rights.
            self.assertEqual(self._acl(self.root)["Sddl"], parent_before)
            self.assertEqual(self._acl(self.private)["Sddl"], private_before)
            self.assertEqual(self._acl(self.pin)["Sddl"], pin_before)
