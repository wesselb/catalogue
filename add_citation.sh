#!/usr/bin/env zsh
set -e

cd /Users/Wessel/Dropbox/Resources

file=$(find -L . | grep .pdf | fzf)
file_json=$(echo $file | sed 's/.pdf/.json/')
echo $file

echo "Press enter to confirm"
read

echo Output:
pbpaste | bib2json | tee
echo

if [ -f "$file_json" ]; then
    echo "Warning: file already exists"
fi
echo "Write to file? ([yes]/no)"
read tmp
if [ "$tmp" = "no" ]; then
    exit 0
fi
pbpaste | bib2json > $file_json

echo "Make corrections? (yes/[no])"
read tmp
if [ "$tmp" = "yes" ]; then
    subl "$file_json"
fi


