import infi.unittest as unittest
from mock import patch
from infi.recipe.application_packager import utils
from ConfigParser import NoSectionError, NoOptionError


class PyPITestCase(unittest.TestCase):
    def test_custom_pypi(self):
        with patch("ConfigParser.ConfigParser") as ConfigParser:
            ConfigParser().get.return_value = "http://pypi.infinidat.com/simple"
            url = utils._get_package_url("zc.buildout")
            self.assertIn("pypi.infinidat.com//media/", url)
            self.assertNotIn("#", url)

    @unittest.parameters.iterate("exception_class", [NoSectionError, NoOptionError])
    def test_official_pypi(self, exception_class):
        with patch("ConfigParser.ConfigParser") as ConfigParser:
            try:
                ConfigParser().get.side_effect = exception_class("x")
            except TypeError:
                ConfigParser().get.side_effect = exception_class("x", "y")
            url = utils._get_package_url("zc.buildout")
            self.assertNotIn("#", url)
