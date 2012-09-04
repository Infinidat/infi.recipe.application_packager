import unittest
from mock import patch
from os import path, curdir

BUILDOUT_SECTION = {
                    'directory': path.abspath(curdir),
                    'eggs-directory': path.abspath(curdir),
                    'download-cache': path.abspath(curdir),
                   }
PROJECT_SECTION = {
                   'version_file': path.abspath(path.join(curdir, 'src', 'infi', 'recipe',
                                                          'application_packager', '__version__.py')),
                   'product_name': 'Amazing Product',
                   'name': 'infi.amazing_product',
                   'company': 'Infinidat',
                   'upgrade_code': 'abc',
                   'long_description': 'long',
                  }
RECIPE_SECTION = {
                   'deb-dependencies': '',
                   'sign-executables-and-msi': 'false',
                   'pfx-file': '/tmp/a',
                   'pfx-password-file': '/tmp/b',
}


BUILDOUT_CFG = dict(buildout=BUILDOUT_SECTION, project=PROJECT_SECTION, pack=RECIPE_SECTION)

class PackagingRecipeTestCase(unittest.TestCase):
    def test_getters(self):
        from infi.recipe.application_packager.base import PackagingRecipe
        recipe = PackagingRecipe(BUILDOUT_CFG, "pack", RECIPE_SECTION)
        self.assertEquals(recipe.get_buildout_dir(), path.abspath(curdir))
        self.assertEquals(recipe.get_download_cache(), path.abspath(curdir))
        self.assertEquals(recipe.get_download_cache_dist(), path.join(path.abspath(curdir), 'dist'))
        self.assertEquals(recipe.get_eggs_directory(), path.abspath(curdir))
        self.assertNotEquals(recipe.get_project_version__short(), None)
        self.assertNotEquals(recipe.get_project_version__long(), None)
        self.assertEquals(recipe.get_working_directory(), path.join(path.abspath(curdir), 'parts'))
        self.assertEquals(recipe.get_deb_dependencies(), '')
        self.assertEquals(recipe.get_product_name(), 'Amazing Product')
        self.assertEquals(recipe.get_project_name(), 'amazing-product')
        self.assertEquals(recipe.get_package_name(), 'amazing-product')
        self.assertEquals(recipe.get_python_module_name(), 'infi.amazing_product')
        self.assertEquals(recipe.get_company_name(), 'Infinidat')
        self.assertEquals(recipe.get_upgrade_code(), 'ABC')
        self.assertEquals(recipe.get_description(), 'long')
        self.assertEquals(recipe.get_platform_arch(), None)
        self.assertEquals(recipe.get_install_dir(), r"C:\Program Files/Infinidat/Amazing Product")
        self.assertEquals(recipe.get_install_prefix(), "/opt/infinidat/amazing-product")
        self.assertEquals(recipe.get_os_string(), None)
        self.assertEquals(recipe.get_script_name("post_install"), None)
        self.assertEquals(recipe.get_script_args("post_install"), '')
        self.assertEquals(recipe.should_sign_files(), False)
        self.assertEquals(recipe.get_pfx_file(), '/tmp/a')
        self.assertEquals(recipe.get_pfx_password_file(), '/tmp/b')
