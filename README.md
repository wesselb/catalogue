# Catalogue
Resource management with Alfred

## Setup
- Install prerequisite `pip` packages: `pip install titlecase`
- Install prerequisite `brew` packages: `brew install trash fzf`
- Install Sublime Text: `brew cask install sublime-text`
- Import `Catalogue.alfredworkflow` into Alfred
    - Set environment variables
- Configure `config.py`

## Usage
Type `r<space>` in Alfred.

## To-Do
- Rework `BibParser`
    - Allowed fields in parsed Bib file
- Sphinx documentation
- Feature: add symlink to current folder
- Feature: rename pdf's automagically
- Feature: process all pdf's in a folder
- Feature: automagically fetch BibTex files

## Issues
- `mdfind` in doesn't follow symlinks.
