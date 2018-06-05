# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import argparse
import os
import re

import catalogue.utils
import clean


def is_arxiv(path):
    return re.match(r'^[0-9\.]{7,}$',
                    os.path.splitext(os.path.basename(path))[0])


def main(args):
    args.files = filter(is_arxiv, catalogue.utils.list_files('.pdf'))
    clean.main(args)


if __name__ == '__main__':
    desc = 'Clean all unprocessed arXiv PDFs.'
    parser = argparse.ArgumentParser(prog='clean_arxiv.py', description=desc)
    main(parser.parse_args())
