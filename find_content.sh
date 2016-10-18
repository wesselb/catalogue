#!/bin/zsh
dir=/Users/Wessel/Dropbox/Resources
mdfind -onlyin $dir $1 \
    | grep ".pdf"
