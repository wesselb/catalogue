#!/bin/zsh
dir=/Users/Wessel/Dropbox/Resources
find -L $dir \
    | grep .pdf \
    | /usr/local/bin/fzf -f "$1"
