__import__('pkg_resources').declare_namespace(__name__)

from ..base import PackagingRecipe
from .. import bff, rpm
import logging

logger = logging.getLogger(__name__)

class Recipe(PackagingRecipe):
    def install(self):
        packages = []
        for manager in (bff, rpm):
            recipe = manager.Recipe(self.buildout, self.__class__.__name__, self.options)
            try:
                packages += recipe.install()
            except NotImplementedError as error:
                logger.warning('Package will not be created: %s', error)
        return packages
