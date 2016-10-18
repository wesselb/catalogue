# Catalogue
Resource management with Alfred

## Setup
- `pip install titlecase`
- `brew install trash fzf`
- `brew cask install sublime-text`
- Import `Resource Management.alfredworkflow` into Alfred.
    - Set environment variable `catalogue_path` to path of repository.
- Configure `config.py`.

## Usage
Type `r<space>` in Alfred.

## To-Do
- Interface using Alfred:
  - Add citation
  - Delete citation
  - Edit citation
- Rework `BibParser`
- Allowed fields in parsed Bib file
- Sphinx documentation


## Issues
- `mdfind` in `find_content.md` doesn't follow symlinks.
