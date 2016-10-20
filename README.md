# Catalogue
Resource management with Alfred

## Setup
- Install prerequisite `pip` packages: ``pip install titlecase`
- Install prerequisite `brew` packages: ``brew install trash fzf`
- `brew cask install sublime-text`
- Import `Catalogue.alfredworkflow` into Alfred.
    - Set environment variables.
- Configure `config.py`.

## Usage
Type `r<space>` in Alfred.

## To-Do
- Rework `BibParser`
- Allowed fields in parsed Bib file
- Sphinx documentation
- Add symlink to current folder
- Rename pdf's automagically
- Process all pdf's in a folder
- Automagically fetch BibTex files

## Issues
- `mdfind` in `find_content.md` doesn't follow symlinks.
