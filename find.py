import argparse

import catalogue.alfred
import catalogue.bin
import catalogue.utils
from config import config


def main(args):
    query = " ".join(args.query)
    if args.json:
        extensions = [".json"]
    else:
        extensions = [".pdf", ".djvu", ".epub"]
    if args.content:
        files = catalogue.bin.mdfind(config["resource_path"], query)
        files = catalogue.utils.file_filter(files, extensions)
    else:
        files = catalogue.bin.fzf(
            "\n".join(catalogue.utils.list_files(extensions)), query
        )
    print(catalogue.alfred.list_json(files, config["base_path"]))


if __name__ == "__main__":
    desc = "Search through names of pdf resources."
    parser = argparse.ArgumentParser(prog="find.py", description=desc)
    parser.add_argument(
        "--content", help="instead search content", action="store_true", default=False
    )
    parser.add_argument(
        "--json", help="instead search json files", action="store_true", default=False
    )
    parser.add_argument("query", nargs="+", help="query to search for")
    main(parser.parse_args())
