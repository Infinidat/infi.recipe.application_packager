import platform
from infi.os_info import get_platform_string, system_is_rhel_based
from infi.recipe.application_packager import aix, deb, msi, pkg, rpm

def get_platform_specific_recipe():
    system = platform.system()
    if system == 'Windows':
        return msi.Recipe
    elif system == 'Linux':
        dist = get_platform_string().split('-')[1]
        if system_is_rhel_based() or dist == 'suse':
            return rpm.Recipe
        elif dist in ['debian', 'ubuntu']:
            return deb.Recipe
        else:
            NotImplementedError('No packaging recipe available for {} Linux distribution'.format(dist))
    elif system == 'SunOS':
        return pkg.Recipe
    elif system == 'AIX':
        return aix.Recipe
    else:
        raise NotImplementedError('No packaging recipe available for {} platform'.format(system))

Recipe = get_platform_specific_recipe()
