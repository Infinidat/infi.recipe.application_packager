# http://fedoraproject.org/wiki/Packaging:ScriptletSnippets
# runs after old package is removed
#           install upgrade  uninstall
# %postun   (N/A)   $1 == 1 $1 == 0

if test -n "$1" -a "$1" != "0"; then
    exit 0
fi

pushd . > /dev/null 2>&1
cd %{prefix}

cleanup_site_packages_and_eggs_directory() {
    find . -type d -name __pycache__ -prune -exec rm -rf  {} \;
    rm -rf parts/python/lib*/python*/site-packages/*  > /dev/null 2>&1
    rm -rf eggs/*ovo > /dev/null 2>&1
    # clean up python 2.7 leftover from older versions
    {% if remove_python %}
        {% if package_arch == "x86_64" %}
            find parts/python/lib64/ -name "python2.*" -type d -prune -exec rm -rf  {} \; > /dev/null 2>&1
        {% else %}
            find parts/python/lib/ -name "python2.*" -type d -prune -exec rm -rf  {} \; > /dev/null 2>&1
        {% endif %}
    {% endif %}
}

cleanup_site_packages_and_eggs_directory

# clean installed directories
# this also deletes installed files
for dirname in {{ directories_to_clean }}; do
{% if aix %}
    rm -rf "$dirname" > /dev/null 2>&1
{% else %}
    find "$dirname" -maxdepth 1 -mindepth 1 -delete > /dev/null 2>&1
{% endif %}
done

cd ..
popd > /dev/null 2>&1

set +e
{% if aix %}
rmdir %{prefix}
{% else %}
rmdir -v %{prefix}
{% endif %}
set -e

exit 0
