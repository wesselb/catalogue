# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import argparse
import json
import os

import catalogue.utils
from config import config
from catalogue.bibtex import decode


def main(args):
    entries = []
    for entry in catalogue.utils.list_files([".json"]):
        with open(entry) as f:
            entries.extend(json.load(f))

    output_dir = os.path.join(config["catalogue_path"], "output")
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    with open(os.path.join(output_dir, "bibliography.bib"), "w") as f:
        f.write(decode(entries))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="update_bibliography.py")
    main(parser.parse_args())
