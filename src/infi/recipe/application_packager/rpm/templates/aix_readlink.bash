# readlink doesn't exist on AIX so we implement it here
# copied from http://gnu-bash.2382.n7.nabble.com/equivalent-of-Linux-readlink-f-in-pure-bash-td10338.html
readlink()
{
    local path="$1"
    test -z "$path" && echo "usage: readlink path" 1>&2 && exit 1;

    local dir

    if test -L "$path"
    then
        local link=$(ls -l "$path" | sed "s/.* -> //")
        if test "$link" = "${link#/}"
        then
            # relative link
            dir="$(dirname "$path")"
            readlink "${dir%/}/$link"
        else
            # absolute link
            readlink "$link"
        fi
    elif test -d "$path"
    then
        (cd "$path"; pwd -P) # normalize it
    else
        dir="$(cd $(dirname "$path"); pwd -P)"
        base="$(basename "$path")"
        echo "${dir%/}/${base}"
    fi
}