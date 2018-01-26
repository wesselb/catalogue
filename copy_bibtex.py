# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import argparse
import json

import core.bin
from core.bibtex import decode


def main(args):
    entries = []
    for entry in args.path:
        with open(entry) as f:
            entries.extend(json.load(f))
    core.bin.pbcopy(decode(entries))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='copy_bibtex.py')
    parser.add_argument('path', help='JSON', nargs='+')
    main(parser.parse_args())
