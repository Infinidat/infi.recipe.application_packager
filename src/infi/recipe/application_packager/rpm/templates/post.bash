# http://fedoraproject.org/wiki/Packaging:ScriptletSnippets
# runs after files of the new package are in place
# the %pre script prepared us for upgrade already
#           install  upgrade  uninstall
#  %post    $1 == 1 $1 == 2 (N/A)

{% include 'header.bash' %}
{% include '_echo.bash' %}

# start
execute pushd .
execute cd %{prefix}

# bootstrap
_echo "Bootstrapping, this may take a few minutes             "
execute parts/python/bin/python bootstrap.py --download-base=.cache/dist --setup-source=.cache/dist/ez_setup.py --index=http://256.256.256.256/
RC=$?
_echo "\r"
assert_rc

# buildout
_echo "Bootstrapping, this may take a few minutes             "
execute bin/buildout -U
RC=$?
_echo "\r"
assert_rc

# link binaries to /usr/bin
execute cd bin
for script in *; do
    if test "$script" == "buildout"; then
        continue;
    fi
    if test -n "%{post_install_script_name}" -a "$script" == "%{post_install_script_name}"; then
        continue;
    fi
    if test -n "%{pre_uninstall_script_name}" -a "$script" == "%{pre_uninstall_script_name}"; then
        continue;
    fi
    _echo "Bootstrapping, this may take a few minutes             "
    execute ln -s -f %{prefix}/bin/$script %{_bindir}/$script
    {% if aix %}
    execute ln -s -f %{prefix}/bin/$script /usr/bin/$script
    {% endif %}
    RC=$?
    _echo "\r"
    assert_rc
done
cd ..

# execute application's post-install script
if test -n "%{post_install_script_name}" -a -x "bin/%{post_install_script_name}"; then
    execute bin/%{post_install_script_name} %{post_install_script_args}
    RC=$?
    assert_rc
fi

#end
execute popd
exit 0
