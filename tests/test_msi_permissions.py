"""MSI action/file wiring tests; no Windows toolchain or package build needed."""

from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, call, patch
import xml.etree.ElementTree as ET

from jinja2 import Environment
from infi.recipe.application_packager import msi


class MsiPermissionsTests(unittest.TestCase):
    def make_recipe(self, timeout=0):
        recipe = object.__new__(msi.Recipe)
        recipe.get_windows_buildout_rename_retry_timeout = Mock(return_value=timeout)
        recipe.get_buildout_dir = Mock(return_value="build directory")
        recipe.get_download_cache_dist = Mock(return_value="cached distributions")
        recipe.add_aditional_directories = Mock()
        recipe.get_script_name = Mock(side_effect={
            "post_install": "application_post_install",
            "pre_uninstall": "application_pre_uninstall",
        }.get)
        recipe.get_script_args = Mock(return_value="")
        wix = Mock()
        wix.installdir = "installation directory"
        wix.add_file.return_value = SimpleNamespace(id="launcher")
        wix.add_deferred_in_system_context_custom_action.side_effect = (
            lambda name, commandline, **kwargs: SimpleNamespace(id="custom_action_" + name)
        )
        return recipe, wix

    def test_helper_is_included_even_without_rename_retry(self):
        for timeout in (0, 60):
            with self.subTest(timeout=timeout):
                recipe, wix = self.make_recipe(timeout)
                recipe._put_all_files(wix, "silent launcher")
                helper = str(Path(msi.__file__).parent.parent / "utils" / "buildout" / "windows_permissions.py")
                self.assertTrue(Path(helper).is_file())
                self.assertIn(call(helper, wix.installdir, "restore-egg-permissions.py"), wix.add_file.call_args_list)

    def test_acl_action_is_after_bootstrap_and_before_post_install(self):
        for timeout in (0, 60):
            with self.subTest(timeout=timeout):
                recipe, wix = self.make_recipe(timeout)
                recipe._append_custom_actions(wix, "launcher")
                recipe._add_project_entry_points(wix, "launcher")
                actions = {
                    item.args[0]: item
                    for item in wix.add_deferred_in_system_context_custom_action.call_args_list
                }
                self.assertEqual(actions["bootstrap"].kwargs["after"], "custom_action_get-pip")
                self.assertEqual(actions["restore_egg_permissions"].kwargs["after"], "custom_action_bootstrap")
                self.assertEqual(actions["application_post_install"].kwargs["after"], "custom_action_restore_egg_permissions")
                self.assertEqual(actions["application_pre_uninstall"].kwargs["before"], "custom_action_close_application")
                for name, action in actions.items():
                    if name.startswith("delete_extra_executables_"):
                        self.assertEqual(action.kwargs["after"], "custom_action_restore_egg_permissions")

    def test_acl_action_does_not_require_an_application_post_install(self):
        recipe, wix = self.make_recipe()
        recipe.get_script_name.return_value = None
        recipe.get_script_name.side_effect = None

        recipe._append_custom_actions(wix, "launcher")
        recipe._add_project_entry_points(wix, "launcher")

        names = [item.args[0] for item in wix.add_deferred_in_system_context_custom_action.call_args_list]
        self.assertIn("restore_egg_permissions", names)
        self.assertNotIn("application_post_install", names)

    def test_helper_runs_with_isolated_stdlib_and_quoted_installation_paths(self):
        recipe, wix = self.make_recipe()

        result = recipe._append_restore_egg_permissions_custom_action(wix, "bootstrap", "launcher")

        self.assertEqual(result, "custom_action_restore_egg_permissions")
        args, kwargs = wix.add_deferred_in_system_context_custom_action.call_args
        self.assertEqual(args, (
            "restore_egg_permissions",
            '"[INSTALLDIR]parts\\python\\bin\\python.exe" -E -S "[INSTALLDIR]restore-egg-permissions.py"',
        ))
        self.assertEqual(kwargs["silent_launcher_file_id"], "launcher")
        self.assertEqual(kwargs["condition"], msi.CONDITION_DURING_EGG_ACL_REPAIR)

    def test_repair_is_supported_without_changing_other_custom_action_conditions(self):
        self.assertEqual(msi.CONDITION_DURING_INSTALL_OR_REPAIR, 'NOT Installed OR MaintenanceMode="Modify"')
        self.assertEqual(msi.CONDITION_DURING_EGG_ACL_REPAIR,
                         '(NOT Installed OR MaintenanceMode="Modify" OR MaintenanceMode="Repair" OR REINSTALL) AND NOT REMOVE="ALL"')

    def test_wix_action_is_system_context_and_checks_failure(self):
        template = Path(msi.__file__).parent / "wix" / "wixcustomaction.inc"
        element = SimpleNamespace(
            id="custom_action_restore_egg_permissions",
            cmd_line='"[INSTALLDIR]parts\\python\\bin\\python.exe" -E -S "[INSTALLDIR]restore-egg-permissions.py"',
            silent_launcher_file_id="launcher",
        )
        xml = Environment(autoescape=True).from_string(template.read_text()).render(element=element)
        action = ET.fromstring(xml)
        self.assertEqual(action.attrib["Execute"], "deferred")
        self.assertEqual(action.attrib["Impersonate"], "no")
        self.assertEqual(action.attrib["Return"], "check")

    def test_no_custom_actions_switch_also_applies_to_acl_repair(self):
        template = Path(msi.__file__).parent / "wix" / "template.wxs"
        source = template.read_text()
        self.assertIn("for element in custom_actions", source)
        self.assertIn("NOT NO_CUSTOM_ACTIONS=&quot;1&quot;", source)


if __name__ == "__main__":
    unittest.main()
