from infi import unittest, pyutils
from pkg_resources import resource_filename
from mock import patch
from os import path, remove
from shutil import rmtree

try:
    import lxml.etree
except ImportError:
    raise unittest.SkipTest("Cannot import lxml.etree")

from ...project_info.tests import BUILDOUT_EXAMPLE, silence_buildout, Buildout, BuildoutProject
from .. import Recipe, Wix
from contextlib import nested

EXPECTED_URLS = ['http://pypi01.infinidat.com/media/dists/distribute_setup.py',
                 'http://pypi01.infinidat.com/media/dists/distribute-0.6.24.tar.gz',
                 'http://pypi01.infinidat.com/media/dists/zc.buildout-1.5.4.tar.gz',
                 'http://bootsrv.infinidat.com/clientapps/vcredist/VisualStudio2008/x64/Microsoft.VC90.CRT/Microsoft.VC90.CRT.manifest',
                 'http://bootsrv.infinidat.com/clientapps/vcredist/VisualStudio2008/x64/Microsoft.VC90.CRT/msvcm90.dll',
                 'http://bootsrv.infinidat.com/clientapps/vcredist/VisualStudio2008/x64/Microsoft.VC90.CRT/msvcp90.dll',
                 'http://bootsrv.infinidat.com/clientapps/vcredist/VisualStudio2008/x64/Microsoft.VC90.CRT/msvcr90.dll',
                 'http://gitserver.infinidat.com/host/authenticode/blobs/raw/master/infinidat_ltd_verisign.pfx',
                 'http://bootsrv.infinidat.com/clientapps/signtool.exe',
                 'http://bootsrv.infinidat.com/clientapps/silent_launcher-x64.exe',
                 'http://bootsrv.infinidat.com/clientapps/wix35-binaries.zip',
                ]

DIRECTORIES = [path.join('.cache', 'dist'),
               path.join('parts', 'python'),
               'src',
               'eggs', ]

from zc.buildout.download import Download

class TestCase(unittest.TestCase):
    @silence_buildout
    def setUp(self):
        buildout = Buildout(BUILDOUT_EXAMPLE, {})
        self._instance = Recipe(buildout, '', buildout.get('pack'))
        self._downloaded_files = set()

    def tearDown(self):
        for file in self._downloaded_files:
            remove(file)

    def test_constructor(self):
        pass

    def _download_side_effect(self, *args, **kwargs):
        url = args[0]
        self.assertIn(url, EXPECTED_URLS)
        local = path.join(self._instance._info.buildout_dir, '.cache', url.split('/')[-1])
        with open(local, 'w') as fd:
            pass
        self._downloaded_files.add(local)
        return [local, None]

    def _add_directory_side_effect(self, *args, **kwargs):
        src = args[0]
        self.assertTrue(any([src.endswith(item) for item in DIRECTORIES]), src)

    def _make_the_candle_side_effect(self, *args, **kwargs):
        self.assertEqual(args[0], 'product.wxs')

    def _light_the_candle_side_effect(self, *args, **kwargs):
        pass

    def test_install(self):
        with nested(patch.object(Recipe, "write_buildout_configuration_file_for_production"),
                    patch.object(Recipe, "_sign_file"),
                    patch("tarfile.TarFile"),
                    patch("zipfile.ZipFile"),):
            with nested(patch.object(BuildoutProject, "_get_platform_arch"),
                        patch.object(BuildoutProject, "_get_os_string"),
                        patch.object(Download, "__call__"),
                        patch.object(Wix, "_add_directory"),
                        patch.object(Wix, "_make_the_candle"),
                        patch.object(Wix, "_light_the_candle"),
                        ) as (get_platform_arch, get_os_string, download, add_directory, make_the_candle, light_the_candle):
                get_os_string.return_value = 'windows-x64'
                get_platform_arch.return_value = 'x64'
                download.side_effect = self._download_side_effect
                add_directory.side_effect = self._add_directory_side_effect
                make_the_candle.side_effect = self._make_the_candle_side_effect
                light_the_candle.side_effect = self._light_the_candle_side_effect
                files = self._instance.install()
                self.assertTrue(files[0].endswith('hello-world-0.0.1-develop-19-gc62dced-windows-x64.msi'))

class IdTestCase(unittest.TestCase):
    def test_new_id__valid_prefix(self):
        from . import Wix
        wix = Wix(None, None, None)
        _id = wix._new_id(".id")
        self.assertEquals(_id, '_id')

