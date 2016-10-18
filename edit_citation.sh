#!/usr/bin/env zsh
set -e

cd /Users/Wessel/Dropbox/Resources
find -L . \
    | grep .json \
    | fzf \
    | tr -d '\n' \
    | xargs -0 -I {} open "{}"

