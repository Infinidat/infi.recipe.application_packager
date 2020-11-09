# http://fedoraproject.org/wiki/Packaging:ScriptletSnippets
# runs before old package is removed
#         install upgrade  uninstall
# %preun  (N/A)   $1 == 1 $1 == 0

{% include 'header.bash' %}

# start
execute pushd .
execute cd %{prefix}

# detect upgrade, we need to run this script only on uninstall
if test -n "$1" -a "$1" != "0"; then
    exit 0
fi

# execute application's pre-uninstall script
if test -n "%{pre_uninstall_script_name}" -a -x "bin/%{pre_uninstall_script_name}"; then
    execute bin/%{pre_uninstall_script_name} %{pre_uninstall_script_args}
    RC=$?
    assert_rc
fi

CLOSE_ON_UPGRADE_OR_REMOVAL={{ close_on_upgrade_or_removal }}

# close application before uninstalling
if test -n "$CLOSE_ON_UPGRADE_OR_REMOVAL" -a "$CLOSE_ON_UPGRADE_OR_REMOVAL" != "0"; then
    execute bin/buildout -U install debug-logging close-application
    RC=$?
    assert_rc
fi

{% if aix %}
{% include 'aix_readlink.bash' %}
{% endif %}

# remove links to binaries from /usr/bin
execute cd bin
for script in *; do
    if test -n "$script" -a -L %{_bindir}/$script -a "`readlink %{_bindir}/$script`" == "%{prefix}/bin/$script"; then
        execute rm -f %{_bindir}/$script
        RC=$?
        assert_rc
    fi
done

# end
execute popd
exit 0
