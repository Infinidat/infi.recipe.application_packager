# http://fedoraproject.org/wiki/Packaging:ScriptletSnippets
# runs after files of the new package are in place
# the %pre script prepared us for upgrade already
#           install  upgrade  uninstall
#  %post    $1 == 1 $1 == 2 (N/A)

{% include 'header.bash' %}
{% include '_echo.bash' %}

cleanup_site_packages_and_eggs_directory() {
    execute rm -rf parts/python/lib*/python*/site-packages/*
    execute rm -rf eggs/*ovo
}

# start
execute pushd .
execute cd %{prefix}

# bootstrap
_echo "Bootstrapping, this may take a few minutes             "
cleanup_site_packages_and_eggs_directory    # clean for upgrades - HPT-2333
export PYTHONPATH=
execute parts/python/bin/python get-pip.py -v --force-reinstall --ignore-installed --upgrade --isolated --no-index --find-links .cache/dist pip setuptools zc.buildout
execute parts/python/bin/python parts/python/bin/buildout -U
RC=$?
_echo "\r"
assert_rc

# link binaries to /usr/bin
execute cd bin
for script in *; do
    for basename in console-script-test gui-script-test replace_console_script script-launcher pip* easy_install*; do
        rm -f "$basename"
    done
done
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
