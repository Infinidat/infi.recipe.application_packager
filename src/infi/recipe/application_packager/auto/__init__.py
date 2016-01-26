import platform

def get_platform_specific_recipe():
    if platform.system() == 'Windows':
        from .. import msi
        return msi.Recipe
    elif platform.system() == 'Linux':
        distro = platform.linux_distribution()[0].lower()
        if distro.startswith('red') or distro.startswith('cent') or distro.startswith('suse'):
            from .. import rpm
            return rpm.Recipe
        elif distro.startswith('ubuntu'):
            from .. import deb
            return deb.Recipe
    elif platform.system() == 'SunOS':
        from .. import pkg
        return pkg.Recipe
    elif platform.system() == "AIX":
        from .. import rpm
        return rpm.Recipe
    else:
        raise NotImplementedError("no packaging recipe available for this platform")

Recipe = get_platform_specific_recipe()
