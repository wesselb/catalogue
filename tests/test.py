# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

# noinspection PyUnresolvedReferences
from . import eq, neq, lt, le, ge, gt, raises, call, ok, lam

from catalogue.bibtex import AuthorEncoder, StringEncoder


def test_authorencoder():
    yield eq, AuthorEncoder().encode('First Last'), ['First Last']
    yield eq, AuthorEncoder().encode('Last, First'), ['First Last']
    yield eq, AuthorEncoder().encode('M. Last, First'), ['First M. Last']
    yield eq, AuthorEncoder().encode('M Last, First'), ['First M. Last']
    yield eq, AuthorEncoder().encode('M L., First'), ['First M. L.']
    yield eq, AuthorEncoder().encode('M-L., First'), ['First M.-L.']
    yield eq, AuthorEncoder().encode('M.-L, First'), ['First M.-L.']
    yield eq, AuthorEncoder().encode('M.-L., First'), ['First M.-L.']
    yield eq, AuthorEncoder().encode('M-Last., First'), ['First M.-Last']
    yield eq, AuthorEncoder().encode('Middle.-Last., First'), \
          ['First Middle-Last']
    yield eq, AuthorEncoder().encode('Middle.-L, First'), \
          ['First Middle-L.']


def test_stringencoder():
    # Test encoding of TeX modifiers.
    for k, v in StringEncoder.tex_mod_map.items():
        yield eq, StringEncoder().encode('pre{{\\{}e}}post'.format(k)), \
              'pre' + (u'e' + v) + 'post'
        yield eq, StringEncoder().decode('pre' + (u'e' + v) + 'post', None), \
              'pre{{\\{}e}}post'.format(k)
