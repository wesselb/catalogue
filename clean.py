# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import argparse
import json
import os

from catalogue.bibtex import encode, is_arxiv, fetch_arxiv_bibtex, \
    generate_file_name


def main(args):
    for path_pdf in args.files:
        # Verify path.
        if not os.path.isfile(path_pdf):
            print('"{}" is not a file.'.format(path_pdf))
        if not os.path.splitext(path_pdf)[1] == '.pdf':
            print('"{}" is not a PDF.'.format(path_pdf))

        # Parse path and determine whether a JSON exists.
        name, _ = os.path.splitext(os.path.basename(path_pdf))
        base = os.path.dirname(path_pdf)
        path_json = os.path.join(base, name + '.json')
        has_json = os.path.isfile(path_json)

        # If JSON is available, load it.
        if has_json:
            with open(path_json) as f:
                bibtex = json.load(f)
        else:
            bibtex = None

        # Check whether the PDF is from arXiv. If so, fetch and update BiBTeX.
        info = is_arxiv(path_pdf)
        if info:
            # Only generate an ID if there is no JSON.
            arxiv_bibtex = encode(fetch_arxiv_bibtex(path_pdf, info),
                                  generate_ids=not has_json)

            # If BiBTeX exists, preserve key, but overwrite BiBTeX.
            if has_json:
                arxiv_bibtex[0]['id'] = bibtex[0]['id']

            # Overwrite BiBTeX.
            bibtex = arxiv_bibtex

        # Determine new paths paths.
        if bibtex:
            name = generate_file_name(bibtex[0])
            new_path_pdf = os.path.join(base, name + '.pdf')
            new_path_json = os.path.join(base, name + '.json')
        else:
            new_path_pdf = path_pdf
            new_path_json = path_json

        # Move PDF and JSON.
        os.rename(path_pdf, new_path_pdf)
        if has_json:
            os.unlink(path_json)
        if bibtex:
            with open(new_path_json, 'w') as f:
                json.dump(bibtex, f, sort_keys=True, indent=4)


if __name__ == '__main__':
    desc = 'Clean PDFs: re-encode BiBTeX, checking arXiv, and rename.'
    parser = argparse.ArgumentParser(prog='clean.py', description=desc)
    parser.add_argument('files', type=str, help='files',
                        action='store', default=False, nargs='+')
    main(parser.parse_args())
