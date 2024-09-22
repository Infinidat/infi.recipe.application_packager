__import__('pkg_resources').declare_namespace(__name__)

from ..base import PackagingRecipe
from .. import bff, rpm

class Recipe(PackagingRecipe):
    def install(self):
        packages = []
        for manager in (bff, rpm):
            recipe = manager.Recipe(self.buildout, self.__class__.__name__, self.options)
            packages += recipe.install()
        return packages
