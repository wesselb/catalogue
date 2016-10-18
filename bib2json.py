#!/usr/local/bin/python

from core.bib import BibParser
import sys


try:
    content = sys.stdin.read()
    print BibParser(content).to_json()
except:
    print 'core.bib.BibParser: Parse error'
