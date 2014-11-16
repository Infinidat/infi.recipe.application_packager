__import__("pkg_resources").declare_namespace(__name__)

from logging import getLogger
from pkg_resources import resource_string
import xml.etree.ElementTree as ET

logger = getLogger(__name__)

def generate_guid():
    try:
        import msilib
        return msilib.UuidCreate()
    except ImportError: # Non-Windows
        return 'ab51f370-7a04-438e-abd2-5e1bee0b7d4d'

ID_INVALID_PATTERN = r"[^A-Za-z0-9_\.]"
ID_INVALID_PREFIX_PETTERN = r"^[^a-z_]"
WIX_TEMPLATE = resource_string(__name__, 'template.wxs')
BYPASS_CUSTOM_ACTION_PROPERTY = "NO_CUSTOM_ACTIONS"


class Wix(object):
    def __init__(self, product_name, product_version, architecture, upgrade_code, description, company_name, documentation_url=None):
        super(Wix, self).__init__()
        self._context = dict(
            product_name=product_name,
            product_version='.'.join(product_version.split('.')[:3]), # MSI supports a three-part version number format
            architecture=architecture,
            upgrade_code=upgrade_code,
            description=description,
            company_name=company_name,
            documentation_url=documentation_url
        )
        xml = self._render_template()
        self._content = self._parse_xml(xml)
        self._used_ids = set()
        self._shortcuts_component = None

    def _render_template(self):
        from jinja2 import Template, StrictUndefined
        template = Template(WIX_TEMPLATE, undefined=StrictUndefined)
        return template.render(self._context)

    def _parse_xml(self, xml):
        return ET.fromstring(xml)

    def _safe_id(self, unsafe_id):
        from re import sub
        new_id = sub(ID_INVALID_PATTERN, '_', unsafe_id).lower()
        return sub(ID_INVALID_PREFIX_PETTERN, '_', new_id)

    def new_id(self, prefix):
        counter = 1
        prefix = self._safe_id(prefix)
        _id = prefix
        while _id in self._used_ids:
            _id = "{}{}".format(prefix, counter)
            counter += 1
        _id = _id[-72:]
        _id = _id if not _id.startswith('.') else '_{}'.format(_id[1:])
        self._used_ids.add(_id)
        return _id

    def new_element(self, tag, attributes, parent_element=None):
        if parent_element is None:
            return ET.Element(tag, attributes)
        return ET.SubElement(parent_element, tag, attributes)

    def new_component(self, id, directory, guid='*'):
        return self.new_element("Component", {"Id": id, "Guid": guid}, directory)

    def _new_file(self, id, src, dst, component):
        return self.new_element("File", {"Id": id, "Source": src, "Checksum": "yes",
                                          "KeyPath": "yes", "Name": dst}, component)

    def add_delete_pyc_component_to_directory(self, directory):
        component = self.new_component(self.new_id('{}_pyc'.format(directory.get('Id'))), directory,
                                        guid=generate_guid())
        self.new_element('RemoveFile', {'Id':component.get('Id'),
                                         'Name': '*.py*', 'On': 'uninstall'}, component)
        self._append_component_to_feature(component, self.feature)

    def add_delete_all_files_on_removal_component_to_directory(self, directory):
        component = self.new_component(self.new_id('{}_remove_all_files'.format(directory.get('Id'))), directory,
                                        guid=generate_guid())
        self.new_element('RemoveFile', {'Id':component.get('Id'), 'Name': '*', 'On': 'uninstall'}, component)
        self._append_component_to_feature(component, self.feature)

    def add_delete_empty_folder_component_to_directory(self, directory):
        component = self.new_component(self.new_id('{}_remove_directory'.format(directory.get('Id'))), directory,
                                        guid=generate_guid())
        self.new_element('RemoveFolder', {'Id':component.get('Id'), 'On': 'uninstall'}, component)
        self._append_component_to_feature(component, self.feature)

    def mkdir(self, name, parent_directory):
        directory = self.new_element("Directory", {"Id": self.new_id(name), "Name": name}, parent_directory)
        self.add_delete_pyc_component_to_directory(directory)
        self.add_delete_all_files_on_removal_component_to_directory(directory)
        self.add_delete_empty_folder_component_to_directory(directory)
        return directory

    def _add_binary(self, source_filepath):
        return self.new_element('Binary', {'Id': self.new_id(path.basename(source_filepath)),
                                            'SourceFile': source_filepath}, self.product)

    def add_directory(self, src, parent_directory, recursive=True, only_directory_tree=False):
        from os import path, listdir
        src = path.abspath(src)
        source_dirname = path.basename(src)
        destination_directory = self.mkdir(source_dirname, parent_directory)
        for filename in listdir(src):
            filepath = path.join(src, filename)
            if path.isfile(filepath):
                if filename.endswith('pyc') or only_directory_tree:
                    continue
                self.add_file(filepath, destination_directory)
            elif recursive:
                self.add_directory(filepath, destination_directory, recursive, only_directory_tree)

    def add_file(self, source_filepath, destination_directory, destination_filename=None):
        """:returns: the file object"""
        from os import path, curdir
        if path.dirname(source_filepath) == '':
            source_filepath = path.join(path.abspath(curdir), source_filepath)
        if destination_filename is None:
            destination_filename = path.basename(source_filepath)
        _id = self.new_id(destination_filename)
        component = self.new_component(_id, destination_directory)
        file_object = self._new_file(_id, source_filepath, destination_filename, component)
        self._append_component_to_feature(component, self.feature)
        return file_object

    def add_environment_variable(self, key, value, component):
        self.new_element("Environment", {'Id': self.new_id(key),
                                            'Action': 'set',
                                            'Name': 'Path',
                                            'Part': 'last',
                                            'Permanent': 'no',
                                            'System': 'yes',
                                            'Value': value}, component)
        self._append_component_to_feature(component, self.feature)

    def add_deferred_in_system_context_custom_action(self, name, cmd_line, fail_on_error=True,
                                                      cwd_dir=r'"[INSTALLDIR]"',
                                                      after='PublishProduct', before=None, condition=None,
                                                      silent_launcher_file_id=None,
                                                      text=None):
        attributes = {'Id': self.new_id('custom_action_{}'.format(name)),
                      'FileKey': silent_launcher_file_id,
                      'ExeCommand': '{} {}'.format(cwd_dir, cmd_line),
                      'Execute': 'deferred',
                      'Impersonate': 'no',
                      'Return': 'check' if fail_on_error else 'ignore'}
        action = self.new_element("CustomAction", attributes, self.product)
        attributes = {"Action": action.get('Id')}
        if after is not None:
            attributes['After'] = after
        if before is not None:
            attributes['Before'] = before
        sequence = self.new_element("Custom", attributes, self.install_execute_sequence)
        if condition is not None:
            sequence.text = '({}) AND (NOT {}="1")'.format(condition, BYPASS_CUSTOM_ACTION_PROPERTY) + \
                            (sequence.text or '')
        if text is not None:
            self.new_element("ProgressText", {"Action": action.get('Id')}, self.ui).text = text
        return action

    def get_shortcuts_component(self):
        if self._shortcuts_component is None:
            self._shortcuts_component = self._new_shortcuts_component()
        return self._shortcuts_component

    def _new_shortcuts_component(self):
        # http://stackoverflow.com/questions/470662/how-to-create-a-multi-level-subfolder-in-start-menu-using-wix
        self.disable_advertised_shortcuts()
        component = self.new_component(self.new_id("shortcuts"), self.application_program_menu_folder)
        for element in [self.company_program_menu_folder, self.application_program_menu_folder]:
            self.new_element("CreateFolder", {"Directory": element.get("Id")}, component)
            self.new_element("RemoveFolder", {"Id": element.get('Id'), "On": "uninstall"}, component)
        self.new_element("RegistryValue", {"Root": "HKLM",
                                           "Key": r"Software\{}\{}".format(self.product.get("Manufacturer"),
                                                                           self.product.get("Name")),
                                           "Name": "Shortcuts",
                                           "Type": "integer",
                                           "Value": "1",
                                           "KeyPath": "yes"}, component)
        self._append_component_to_feature(component, self.feature)
        return component

    def add_shortcut(self, shortcut_name, executable_name, icon=None):
        attributes = {'Id': self.new_id('shortcut_{}'.format(shortcut_name)),
                      'Name': shortcut_name,
                      'Description': shortcut_name,
                      'Advertise': 'no',
                      'Target': r'[INSTALLDIR]bin\{}.exe'.format(executable_name),
                      'WorkingDirectory': 'INSTALLDIR',
                     }
        if icon is not None:
            attributes['Icon'] = icon.get("Id")
        shortcut = self.new_element("Shortcut", attributes, self.get_shortcuts_component())

    def new_icon(self, icon_path):
        from os.path import basename
        filename = basename(icon_path)
        extension = '.' + filename.split('.')[-1]
        icon_id = self.new_id(filename.replace(extension, ''))
        icon_id += extension
        return self.new_element("Icon" , {"Id": icon_id, "SourceFile": icon_path}, self.product)

    def set_add_remove_programs_icon(self, icon_path):
        icon_id = self.new_icon(icon_path)
        return self.new_element("Property", {"Id":"ARPPRODUCTICON", "Value":icon_id.get("Id")}, self.product)

    def get_msi_property(self, name):
        for element in self.product.getchildren():
            if element.tag.endswith("Property") and element.get("Id") == name:
                return element

    def add_existing_install_dir(self, root, key, name):
        # http://stackoverflow.com/questions/12576807/how-to-set-targetdir-or-installdir-from-a-registry-entry
        element = self.new_element("Property", {"Id":"EXISTINGINSTALLDIR"}, self.product)
        search_key = self.new_element("RegistrySearch", {"Id": "Locate_EXISTINGINSTALLDIR", "Root": root,
                                                         "Key": key, "Name": name, "Type": "directory"}, element)
        message = "Installation location in registry is missing: {}\\{}\\{}".format(root, key, name)
        condition = self.new_element("Condition", {'Message': message}, self.product)
        condition.text = "EXISTINGINSTALLDIR"

    def set_custom_install_dir(self, value):
        # http://stackoverflow.com/questions/12576807/how-to-set-targetdir-or-installdir-from-a-registry-entry
        attributes = {'Id': "Set_INSTALLDIR", "Execute": "firstSequence", "Property": "INSTALLDIR", "Value": value}
        action = self.new_element("CustomAction", attributes, self.product)
        attributes = {"Action": action.get('Id')}
        sequence = self.new_element("Custom", {"Action": action.get('Id'), "After": "FileCost"}, self.install_execute_sequence)
        sequence.text = "(NOT Installed) AND (EXISTINGINSTALLDIR) AND (NOT UPGRADINGPRODUCTCODE)"
        sequence = self.new_element("Custom", {"Action": action.get('Id'), "After": "FileCost"}, self.install_ui_sequence)
        sequence.text = "(NOT Installed) AND (EXISTINGINSTALLDIR) AND (NOT UPGRADINGPRODUCTCODE)"

    def prevent_user_from_choosing_installation_directory(self):
        next = {"Dialog": "WelcomeDlg", "Control":"Next", "Event": "NewDialog", "Value": "InstallDirDlg"}
        previous = {"Dialog": "VerifyReadyDlg", "Control":"Back", "Event": "NewDialog", "Value": "InstallDirDlg"}
        for item in self.ui.iterchildren():
            if item.tag.endswith("Publish"):
                if all(item.attrib.get(key) == value for key, value in next.iteritems()):
                    item.attrib["Value"] = "VerifyReadyDlg"
                elif all(item.attrib.get(key) == value for key, value in previous.iteritems()):
                    item.attrib["Value"] = "WelcomeDlg"

    def set_msi_property(self, key, value):
        element = self.get_msi_property(key)
        if element is None:
            element = self.new_element("Property", {"Id":key, "Value": value}, self.product)
        element.set("Value", value)
        return element

    def set_allusers(self):
        return self.set_msi_property("ALLUSERS", "1")

    def disable_advertised_shortcuts(self):
        return self.set_msi_property("DISABLEADVTSHORTCUTS", "1")

    def _append_component_to_feature(self, component, feature):
        _ = self.new_element("ComponentRef", {"Id": component.get('Id')}, feature)

    @property
    def product(self):
        return self._content[0]

    @property
    def fragment(self):
        return self._content[1]

    @property
    def ui(self):
        return self.fragment[0]

    @property
    def package(self):
        return self.product[0]

    @property
    def targetdir(self):
        return self.product[2]

    @property
    def programfiles(self):
        return self.targetdir[0]

    @property
    def program_menu_folder(self):
        return self.targetdir[1]

    @property
    def company_root_directory(self):
        return self.programfiles[0]

    @property
    def installdir(self):
        return self.company_root_directory[0]

    @property
    def company_program_menu_folder(self):
        return self.program_menu_folder[0]

    @property
    def application_program_menu_folder(self):
        return self.company_program_menu_folder[0]

    @property
    def feature(self):
        return self.product[3]

    @property
    def install_execute_sequence(self):
        return self.product[6]

    @property
    def install_ui_sequence(self):
        return self.product[7]

    def build(self, wix_basedir, input_file, output_file):
        from ...utils.execute import execute_assert_success
        from os import path
        candle = path.join(wix_basedir, "candle.exe")
        light = path.join(wix_basedir, "light.exe")
        execute_assert_success([candle, input_file, '-arch', self._context['architecture']])
        execute_assert_success([light, '-sval', '-ext', 'WixUIExtension', '-ext', 'WixUtilExtension', '-cultures:en-us',
                               'product.wixobj', '-o', output_file])
