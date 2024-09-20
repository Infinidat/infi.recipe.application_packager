import platform
from infi.os_info import get_platform_string, system_is_rhel_based

def get_platform_specific_recipe():
    system = platform.system()
    if system == 'Windows':
        from .. import msi
        return msi.Recipe
    elif system == 'Linux':
        dist = get_platform_string().split('-')[1]
        if system_is_rhel_based() or dist == 'suse':
            from .. import rpm
            return rpm.Recipe
        elif dist in ('debian', 'ubuntu'):
            from .. import deb
            return deb.Recipe
        else:
            NotImplementedError("no packaging recipe available for %s Linux distribution" % dist)
    elif system == 'SunOS':
        from .. import pkg
        return pkg.Recipe
    elif system == "AIX":
        from .. import aix
        return aix.Recipe
    else:
        raise NotImplementedError("no packaging recipe available for %s platform" % system)

Recipe = get_platform_specific_recipe()
