import json
import core.bin as bin
from core.bib import BibRenderer
import argparse


def main(args):
    entries = []
    for entry in bin.list(['.json']):
        with open(entry) as f:
            entries.extend(json.load(f))

    with open('output/bibliography.bib', 'w') as f:
        f.write(BibRenderer(entries).as_text())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='update_bibliography.py')
    main(parser.parse_args())
