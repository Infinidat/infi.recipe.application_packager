{% if aix %}
# \c disables newline
# other backslash characters like \r are interpreted correctly
_echo() { /usr/bin/echo $@"\c"; }
{% else %}
# -n disables newline
# -e causes backslash characters like \r to be interpreted correctly
_echo() { echo -en $@; }
{% endif %}
