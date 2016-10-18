import argparse
import core.bin as bin
import os
import time
from config import config


def main(args):
    json_file = bin.fzf('\n'.join(bin.list(['.json'])))
    if not json_file or not os.path.isfile(json_file[0]):
        exit()
    print('Are you sure that you want to delete {}? (y/[n])'
          .format(json_file[0]))
    answer = raw_input()
    if answer == 'y':
        bin.trash(json_file[0])
        print '{} deleted.'.format(json_file[0])
        time.sleep(config['feedback_sleep'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='delete_citation.py')
    main(parser.parse_args())
