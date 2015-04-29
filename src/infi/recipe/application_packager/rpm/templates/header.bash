RC=0

assert_rc() {
    if test $RC -ne 0; then
        exit 1
    fi
}

execute() {
    if test $DEBUG -eq 0; then
        $@ > /dev/null 2>&1
    else
        $@
    fi
}

# debugging
DEBUG=0
if test -n "$DEBUG_CUSTOM_ACTIONS" -a "$DEBUG_CUSTOM_ACTIONS" == "1"; then
    DEBUG=1
    set -xv
fi

# bypass custom actions
if test -n "$NO_CUSTOM_ACTIONS" -a "$NO_CUSTOM_ACTIONS" != "0"; then
    exit 0
fi
