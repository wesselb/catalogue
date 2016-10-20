import argparse
import core.bin as bin
from core.utils import ext_change
from core.bib import BibParser


def main(args):
    out = BibParser(bin.pbpaste()).to_json()
    print out
    if args.write:
        json_file = ext_change(args.write, '.json')
        with open(json_file, 'w') as f:
            f.write(out)
        if args.edit:
            bin.subl(json_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='pbpaste2json.py')
    parser.add_argument('--write', help='write for pdf',
                        action='store', default=False)
    parser.add_argument('--edit', help='edit file after writing',
                        action='store_true', default=False)
    main(parser.parse_args())
