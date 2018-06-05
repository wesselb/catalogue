# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import argparse
import json

import catalogue.bin
from catalogue.bibtex import encode
from catalogue.utils import ext_change


def main(args):
    out = json.dumps(encode(catalogue.bin.pbpaste(), generate_ids=True),
                     indent=4, sort_keys=True)
    print(out)
    if args.write:
        json_file = ext_change(args.write, '.json')
        with open(json_file, 'w') as f:
            f.write(out)
        if args.edit:
            catalogue.bin.subl(json_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='pbpaste2json.py')
    parser.add_argument('--write', help='write for pdf',
                        action='store', default=False)
    parser.add_argument('--edit', help='edit file after writing',
                        action='store_true', default=False)
    main(parser.parse_args())
