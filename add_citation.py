import argparse
import core.bin as bin
from core.utils import ext_change
from core.bib import BibParser
import os
from config import config
import time


def main(args):
    # Find entry
    pdf_file = bin.fzf('\n'.join(bin.list(['.pdf'])))
    if not pdf_file or not os.path.isfile(pdf_file[0]):
        exit()
    print 'File: {}'.format(pdf_file[0])
    try:
        out = BibParser(bin.pbpaste()).to_json()
        print 'Parsed entry:\n{}\n'.format(out)
    except:
        print 'Parse error'
        time.sleep(config['feedback_sleep'])
        exit()

    # Write entry
    json_file = ext_change(pdf_file[0], '.json')
    if os.path.isfile(json_file):
        print 'Overwrite current entry? ([y]/n)'
    else:
        print 'Write entry? ([y]/n)'
    answer = raw_input()
    if not (answer == 'y' or answer == ''):
        exit()
    with open(json_file, 'w') as f:
        f.write(out)

    # Edit afterwards
    print 'Edit entry? (y/[n])'
    answer = raw_input()
    if answer == 'y':
        bin.subl(json_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='edit_citation.py')
    main(parser.parse_args())
