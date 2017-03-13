__import__("pkg_resources").declare_namespace(__name__)

from logging import getLogger
from jinja2 import Environment, PackageLoader, StrictUndefined
import os

logger = getLogger(__name__)

def generate_guid():
    try:
        import msilib
        return msilib.UuidCreate()
    except ImportError: # Non-Windows
        return 'ab51f370-7a04-438e-abd2-5e1bee0b7d4d'

ID_INVALID_PATTERN = r"[^A-Za-z0-9_\.]"
ID_INVALID_PREFIX_PATTERN = r"^[^a-z_]"

JINJA_ENV = Environment(loader=PackageLoader('infi.recipe.application_packager.msi', 'wix'),
                        extensions=['jinja2.ext.with_'],
                        autoescape=True,
                        undefined=StrictUndefined)

class WixElement(object):

    def __str__(self):
        return ' '.join([self.__class__.__name__, getattr(self, 'id', ''), getattr(self, 'name', '')])

    def get_template(self):
        return self.__class__.__name__.lower() + '.inc'


class WixContainer(WixElement):

    def __init__(self):
        self.children = []

    def add(self, child):
        assert child is not self
        self.children.append(child)


class WixDirectory(WixContainer):

    def __init__(self, id, name):
        super(WixDirectory, self).__init__()
        self.id = id
        self.name = name


class WixComponent(WixContainer):

    def __init__(self, id, guid):
        super(WixComponent, self).__init__()
        self.id = id
        self.guid = guid


class WixFile(WixElement):

    def __init__(self, id, name, source):
        self.id = id
        self.name = name
        self.source = source


class WixRemoveFile(WixElement):

    def __init__(self, id, name):
        self.id = id
        self.name = name


class WixRemoveFolder(WixElement):

    def __init__(self, id):
        self.id = id


class WixEnvironment(WixElement):

    def __init__(self, id, value):
        self.id = id
        self.value = value


class WixCondition(WixElement):

    def __init__(self, message, condition):
        self.message = message
        self.condition = condition


class WixCustomAction(WixElement):

    def __init__(self, id, name, cmd_line, after='PublishProduct', before=None, condition=None, silent_launcher_file_id=None, text=None):
        self.id = id
        self.name = name
        self.cmd_line = cmd_line
        self.after = after
        self.before = before
        self.condition = condition
        self.silent_launcher_file_id = silent_launcher_file_id
        self.text = text


class WixVariable(WixElement):

    def __init__(self, id, value):
        self.id = id
        self.value = value


class WixIcon(WixElement):

    def __init__(self, id, source):
        self.id = id
        self.source = source


class WixShortcut(WixElement):

    def __init__(self, id, shortcut_name, executable_name, icon_id):
        self.id = id
        self.shortcut_name = shortcut_name
        self.executable_name = executable_name
        self.icon_id = icon_id


class Wix(object):
    def __init__(self, product_name, product_version, architecture, upgrade_code, description, company_name,
                 documentation_url=None, arp_icon_path=None, existing_installdir_registry_key=None, custom_installdir=None):
        super(Wix, self).__init__()
        self._used_ids = set()
        self._context = dict(
            product_name=product_name,
            product_version='.'.join(product_version.split('.')[:3]), # MSI supports a three-part version number format
            architecture=architecture,
            upgrade_code=upgrade_code,
            description=description,
            company_name=company_name,
            documentation_url=documentation_url,
            user_can_choose_installation_directory=False,
            custom_installdir=custom_installdir,
            arp_icon_id=None,
            installdir=WixDirectory('INSTALLDIR', product_name),
            features=[],
            custom_actions=[],
            variables=[],
            conditions=[],
            icons=[],
            shortcuts=[]
        )
        self._add_delete_all_files_on_removal_component_to_directory(self.installdir)
        self._add_delete_empty_folder_component_to_directory(self.installdir)
        if arp_icon_path:
            self._context['arp_icon_id'] = self.add_icon(arp_icon_path)
        self._set_existing_installdir_registry_key(existing_installdir_registry_key)

    def to_xml(self):
        import xml.dom.minidom
        raw_xml = JINJA_ENV.get_template('template.wxs').render(self._context)
        xml = xml.dom.minidom.parseString(raw_xml).toprettyxml() # beautify xml (also ensures it's well formed)
        return '\n'.join([line for line in xml.splitlines() if line.strip()]) # remove empty lines

    def _safe_id(self, unsafe_id):
        from re import sub
        new_id = sub(ID_INVALID_PATTERN, '_', unsafe_id).lower()
        return sub(ID_INVALID_PREFIX_PATTERN, '_', new_id)

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

    def new_component(self, id, directory, guid='*'):
        component = WixComponent(id, guid)
        self._context['features'].append(component)
        directory.add(component)
        return component

    def _add_delete_all_files_on_removal_component_to_directory(self, directory):
        component = self.new_component(self.new_id('{}_remove_all_files'.format(directory.id)), directory,
                                        guid=generate_guid())
        component.add(WixRemoveFile(component.id, '*'))

    def _add_delete_empty_folder_component_to_directory(self, directory):
        component = self.new_component(self.new_id('{}_remove_directory'.format(directory.id)), directory,
                                        guid=generate_guid())
        component.add(WixRemoveFolder(component.id))

    def mkdir(self, name, parent_directory):
        directory = WixDirectory(self.new_id(name), name)
        parent_directory.add(directory)
        self._add_delete_all_files_on_removal_component_to_directory(directory)
        self._add_delete_empty_folder_component_to_directory(directory)
        return directory

    def add_directory(self, src, parent_directory, recursive=True, only_directory_tree=False, include_pyc=False):
        from os import path, listdir
        src = path.abspath(src)
        source_dirname = path.basename(src)
        destination_directory = self.mkdir(source_dirname, parent_directory)
        for filename in listdir(src):
            filepath = path.join(src, filename)
            if path.isfile(filepath):
                if only_directory_tree:
                    continue
                if filename.endswith('.pyc') and not include_pyc:
                    continue
                self.add_file(filepath, destination_directory)
            elif recursive:
                self.add_directory(filepath, destination_directory, recursive, only_directory_tree, include_pyc)

    def add_file(self, source_filepath, destination_directory, destination_filename=None):
        from os import path, curdir
        if path.dirname(source_filepath) == '':
            source_filepath = path.join(path.abspath(curdir), source_filepath)
        if destination_filename is None:
            destination_filename = path.basename(source_filepath)
        _id = self.new_id(destination_filename)
        file_object = WixFile(_id, destination_filename, source_filepath)
        component = self.new_component(_id, destination_directory)
        component.add(file_object)
        return file_object

    def add_environment_variable(self, key, value, component):
        component.add(WixEnvironment(key, value))

    def add_deferred_in_system_context_custom_action(self, name, cmd_line, fail_on_error=True,
                                                      cwd_dir=r'"[INSTALLDIR]"',
                                                      after='PublishProduct', before=None, condition=None,
                                                      silent_launcher_file_id=None,
                                                      text=None):
        action = WixCustomAction(self.new_id('custom_action_{}'.format(name)), name, cmd_line,
                                 after=after, before=before, condition=condition,
                                 silent_launcher_file_id=silent_launcher_file_id, text=text)
        self._context['custom_actions'].append(action)
        return action

    def add_shortcut(self, shortcut_name, executable_name, icon_id=None):
        id = self.new_id('shortcut_{}'.format(shortcut_name))
        self._context['shortcuts'].append(WixShortcut(id, shortcut_name, executable_name, icon_id))

    def add_icon(self, icon_path):
        filename = os.path.basename(icon_path)
        extension = '.' + filename.split('.')[-1]
        icon_id = self.new_id(filename.replace(extension, '')) + extension
        self._context['icons'].append(WixIcon(icon_id, icon_path))
        return icon_id

    def add_variable(self, id, value):
        self._context['variables'].append(WixVariable(id, value))

    def add_condition(self, message, condition):
        self._context['conditions'].append(WixCondition(message, condition))

    def _set_existing_installdir_registry_key(self, existing_installdir_registry_key):
        # See http://stackoverflow.com/questions/12576807/how-to-set-targetdir-or-installdir-from-a-registry-entry
        if existing_installdir_registry_key:
            root, key = existing_installdir_registry_key.split("\\", 1) # HKLM, SOFTWARE\...\InstallPath
            key, name = key.rsplit("\\", 1) # Software...\, InstallPath
            self._context['existing_installdir_registry_key'] = (root, key, name)
            message = "Installation location in registry is missing: " + existing_installdir_registry_key
            self.add_condition(message, "EXISTINGINSTALLDIR")
        else:
            self._context['existing_installdir_registry_key'] = None

    @property
    def installdir(self):
        return self._context['installdir']

    def build(self, wix_basedir, input_file, output_file):
        from ...utils.execute import execute_assert_success
        from os import path
        candle = path.join(wix_basedir, "candle.exe")
        light = path.join(wix_basedir, "light.exe")
        execute_assert_success([candle, input_file, '-arch', self._context['architecture']])
        execute_assert_success([light, '-sval', '-ext', 'WixUIExtension', '-ext', 'WixUtilExtension', '-cultures:en-us',
                               'product.wixobj', '-o', output_file])
