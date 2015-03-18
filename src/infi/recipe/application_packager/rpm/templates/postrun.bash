# http://fedoraproject.org/wiki/Packaging:ScriptletSnippets
# runs after old package is removed
#           install upgrade  uninstall
# %postun   (N/A)   $1 == 1 $1 == 0

if test -n "$1" -a "$1" != "0"; then
    exit 0
fi

set +e
{% if aix %}
rmdir %{prefix}
{% else %}
rmdir -v %{prefix}
{% endif %}
set -e

exit 0
