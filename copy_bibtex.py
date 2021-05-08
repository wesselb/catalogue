import argparse
import json

import catalogue.bin
from catalogue.bibtex import decode


def main(args):
    entries = []
    for entry in args.path:
        with open(entry) as f:
            entries.extend(json.load(f))
    catalogue.bin.pbcopy(decode(entries))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="copy_bibtex.py")
    parser.add_argument("path", help="JSON", nargs="+")
    main(parser.parse_args())
