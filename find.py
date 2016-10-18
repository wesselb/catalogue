from core.alfred import AlfredFormatter
import argparse
import core.bin as bin
from config import config


def main(args):
    query = args.query[0]
    if args.content:
        files = bin.mdfind(config['resource_path'], query)
    else:
        files = bin.fzf('\n'.join(bin.list(['.pdf'])), query)
    print AlfredFormatter(files, config['base_path']).list_json()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='find.py')
    parser.add_argument('--content', help='search content',
                        action='store_true', default=False)
    parser.add_argument('query', nargs='+', help='query to search for')
    main(parser.parse_args())
