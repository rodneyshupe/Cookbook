#!/usr/bin/env bash

# TODO: check if pyenv is installed if so install latest python
get_version() {
    if command -v pyenv 1>/dev/null 2>&1; then
        local query=${1:-[0-9]}
        [[ -z $query ]] && query=$DEFAULT_QUERY
        pyenv install --list \
            | grep -vE "(^Available versions:|-src|dev|rc|alpha|beta|(a|b)[0-9]+)" \
            | grep -E "^\s*$query" \
            | sed 's/^\s\+//' \
            | tail -1
    fi
}

if command -v pyenv 1>/dev/null 2>&1; then
    pyenv install $(get_version)
fi

python -m pip install --upgrade pip
python -m pip install --upgrade rst2pdf 
python -m pip install --upgrade rst2html
python -m pip install --upgrade rst2html5

# TODO: need to make this cross platform.
brew install calibre
