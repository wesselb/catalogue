import json
import core.bin as bin
from core.bib import BibRenderer
from config import config
import argparse
import os


def main(args):
    entries = []
    for entry in bin.list(['.json']):
        with open(entry) as f:
            entries.extend(json.load(f))

    output_dir = os.path.join(config['catalogue_path'], 'output')
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    with open(os.path.join(output_dir, 'bibliography.bib'), 'w') as f:
        f.write(BibRenderer(entries).as_text())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='update_bibliography.py')
    main(parser.parse_args())
