#!/usr/bin/env bash
cd /Users/Wessel/Dropbox/Resources
find -L . \
    | grep .pdf \
    | fzf \
    | tr -d '\n' \
    | xargs -0 -I {} open "{}"
