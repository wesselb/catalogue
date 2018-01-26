# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import argparse

import core.alfred
import core.bin
import core.utils
from config import config


def main(args):
    query = ' '.join(args.query)
    if args.json:
        extensions = ['.json']
    else:
        extensions = ['.pdf', '.djvu', '.epub']
    if args.content:
        files = core.bin.mdfind(config['resource_path'], query)
        files = core.utils.file_filter(files, extensions)
    else:
        files = core.bin.fzf('\n'.join(core.bin.list(extensions)), query)
    print(core.alfred.list_json(files, config['base_path']))


if __name__ == '__main__':
    desc = 'Search through names of pdf resources.'
    parser = argparse.ArgumentParser(prog='find.py', description=desc)
    parser.add_argument('--content', help='instead search content',
                        action='store_true', default=False)
    parser.add_argument('--json', help='instead search json files',
                        action='store_true', default=False)
    parser.add_argument('query', nargs='+', help='query to search for')
    main(parser.parse_args())
