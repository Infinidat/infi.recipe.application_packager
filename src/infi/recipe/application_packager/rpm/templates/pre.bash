# http://fedoraproject.org/wiki/Packaging:ScriptletSnippets
# runs before a new package is installed
#       install  upgrade  uninstall
# %pre  $1 == 1 $1 == 2 (N/A)

{% include 'header.bash' %}
{% include '_echo.bash' %}

LONG_BIT="$(getconf LONG_BIT)"

# prevent installation of 32bit packages on 64bit systems
if test -n "$LONG_BIT" -a "$LONG_BIT" == "64" -a \( "%{target_arch}" == "i386" -o "%{target_arch}" == "i686" \) ; then
    echo package %{package_name}-%{package_version}-1.%{target_arch} is intended for a %{target_arch} architecture 1>&2;
    exit 1
fi

# if target dir exists
if test -d %{prefix}; then
    # in case of an upgrade
    if test -n "$1" -a "$1" != "1"; then

        execute pushd .
        execute cd %{prefix}

        CLOSE_ON_UPGRADE_OR_REMOVAL={{ close_on_upgrade_or_removal }}

        # close application before the upgrade
        if test -n "$CLOSE_ON_UPGRADE_OR_REMOVAL" -a "$CLOSE_ON_UPGRADE_OR_REMOVAL" != "0"; then
            execute parts/python/bin/python get-pip.py -v --force-reinstall --ignore-installed --upgrade --isolated --no-index --find-links .cache/dist
            execute bin/buildout -U install debug-logging close-application
            RC=$?
            assert_rc
        fi

        # if source directory exists, we need to delete since the files of the old package
        # will be deleted only after the %post
        if test -d src; then
            _echo "\rRemoving stale cache files, this may take a few minutes"
            execute rm -rf src
            _echo "\r"
        fi

        # delete old eggs
        _echo "\rRemoving temporary files, this may take a few minutes  "
        execute rm -rvf eggs
        _echo "\r"

        execute popd
    fi
fi

exit 0
