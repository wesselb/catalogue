import argparse
import core.bin as bin
import os


def main(args):
    json_file = bin.fzf('\n'.join(bin.list(['.json'])))
    if json_file and os.path.isfile(json_file[0]):
        bin.subl(json_file[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='edit_citation.py')
    main(parser.parse_args())
