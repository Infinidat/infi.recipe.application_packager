import platform

def get_platform_specific_recipe():
    if platform.system() == 'Windows':
        from .. import msi
        return msi.Recipe
    elif platform.system() == 'Linux':
        distro = platform.linux_distribution()[0].lower()
        if distro.startswith('red') or distro.startswith('cent'):
            from .. import rpm
            return rpm.Recipe
        elif distro.startswith('ubuntu'):
            from .. import deb
            return deb.Recipe
    else:
        return None

Recipe = get_platform_specific_recipe()
