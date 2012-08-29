from infi import unittest, pyutils
from pkg_resources import resource_filename
from mock import patch
from os import path, remove
from shutil import rmtree

from ...project_info.tests import BUILDOUT_EXAMPLE, silence_buildout, Buildout, BuildoutProject
from .. import Recipe, Project
from contextlib import nested

EXPECTED_URLS = ['http://pypi01.infinidat.com/media/dists/distribute_setup.py',
                 'http://pypi01.infinidat.com/media/dists/distribute-0.6.24.tar.gz',
                 'http://pypi01.infinidat.com/media/dists/zc.buildout-1.5.4.tar.gz',
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

    def test_install(self):
        with nested(patch.object(Recipe, "write_buildout_configuration_file_for_production"),
                    patch("tarfile.TarFile"),
                    patch("zipfile.ZipFile"),
                    patch("shutil.copy"),
                    patch.object(Project, "_call_dpkg")):
            with nested(patch.object(BuildoutProject, "_get_platform_arch"),
                        patch.object(BuildoutProject, "_get_os_string"),
                        patch.object(Download, "__call__"),
                        patch.object(Project, "_add_directory"),
                        ) as (get_platform_arch, get_os_string, download, add_directory):
                get_os_string.return_value = 'linux-ubuntu-11.04-x64'
                get_platform_arch.return_value = 'x64'
                download.side_effect = self._download_side_effect
                add_directory.side_effect = self._add_directory_side_effect
                files = self._instance.install()
                self.assertTrue(files[0].endswith('hello-world-0.0.1-develop-19-gc62dced-linux-ubuntu-11.04-x64.deb'),
                                files[0])
