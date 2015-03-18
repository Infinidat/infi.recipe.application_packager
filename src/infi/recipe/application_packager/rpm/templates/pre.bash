# http://fedoraproject.org/wiki/Packaging:ScriptletSnippets
# runs before a new package is installed
#       install  upgrade  uninstall
# %pre  $1 == 1 $1 == 2 (N/A)

{% include 'header.bash' %}

# if target dir exists
if test -d %{prefix}; then
    # in case of an upgrade
    if test -n "$1" -a "$1" != "1"; then

        execute pushd .
        execute cd %{prefix}

        CLOSE_ON_UPGRADE_OR_REMOVAL={{ close_on_upgrade_or_removal }}

        # close application before the upgrade
        if test -n "$CLOSE_ON_UPGRADE_OR_REMOVAL" -a "$CLOSE_ON_UPGRADE_OR_REMOVAL" != "0"; then
            execute bin/buildout -U install debug-logging close-application
            RC=$?
            assert_rc
        fi

        # if source directory exists, we need to delete since the files of the old package
        # will be deleted only after the %post
        if test -d src; then
            echo -en "\rRemoving stale cache files, this may take a few minutes"
            execute rm -rf src
            echo -en "\r"
        fi

        # delete old eggs
        echo -en "\rRemoving temporary files, this may take a few minutes"
        execute rm -rvf eggs
        echo -en "\r"

        execute popd
    fi
fi

exit 0