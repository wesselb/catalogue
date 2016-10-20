from core.alfred import AlfredFormatter
import argparse
import core.bin as bin
from config import config
import core.utils


def main(args):
    query = ' '.join(args.query)
    if args.json:
        extensions = ['.json']
    else:
        extensions = ['.pdf']
    if args.content:
        files = bin.mdfind(config['resource_path'], query)
        files = core.utils.filter_ext(files, extensions)
    else:
        files = bin.fzf('\n'.join(bin.list(extensions)), query)
    print AlfredFormatter(files, config['base_path']).list_json()


if __name__ == '__main__':
    desc = 'Search through names of pdf resources'
    parser = argparse.ArgumentParser(prog='find.py', description=desc)
    parser.add_argument('--content', help='instead search content',
                        action='store_true', default=False)
    parser.add_argument('--json', help='instead search json files',
                        action='store_true', default=False)
    parser.add_argument('query', nargs='+', help='query to search for')
    main(parser.parse_args())
