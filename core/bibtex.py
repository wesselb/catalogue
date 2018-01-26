# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import abc
import datetime
import re
import unicodedata
import urllib2
import warnings
from string import uppercase, lowercase, digits
from subprocess import Popen, PIPE

import bibtexparser as bp
from bs4 import BeautifulSoup
from titlecase import titlecase
from config import config

__all__ = ['is_arxiv', 'fetch_arxiv_bibtex', 'encode', 'decode',
           'generate_file_name']


def is_arxiv(fp):
    """
    Check whether a PDF is from arXiv.

    Args:
        fp: File path.

    Returns:
        `None` if the PDF is not from arXiv and the detected arXiv identifier
        otherwise.

    """
    # Attempt to extract the arXiv number via `pdfgrep`.
    process = Popen([config['binaries']['pdfgrep'],
                     '-m', '1', '-h', 'arXiv', fp],
                    stdout=PIPE)
    out = process.communicate()[0].strip()
    res = re.match(r'arXiv:([a-zA-Z\-]*)\/?([0-9\.]+)v([0-9]+) '
                   r'\[?([0-9a-zA-Z. _\-]+)\]?', out)
    if res:
        cat, num, _, _ = res.groups()
        return cat, num
    return None


def fetch_arxiv_bibtex(fp, info=None):
    """
    Fetch the BiBTeX for an arXiv PDF.

    Args:
        fp: Path.
        info (optional): arXiv info from :method:`.bibtex.is_arxiv`.

    Returns:
        The BiBTeX if it can be found and `None` otherwise.
    """
    info = info if info else is_arxiv(fp)

    if info:
        cat, num = info

        # Successful. Now fetch the BiBTeX.
        page = urllib2.urlopen('http://adsabs.harvard.edu/cgi-bin/bib_query?'
                               'arXiv:{}{}'.format(cat + '/' if cat else '',
                                                   num)).read()
        soup = BeautifulSoup(page, 'html5lib')
        el = soup.find('a', text='Bibtex entry for this abstract', href=True)
        href = urllib2.urlopen(el['href']).read()

        # Skip until the first '@', which should mark the beginning of the
        # BiBTeX.
        return '@' + '@'.join(href.split('@')[1:])
    return None


def str_for_file(xs):
    """
    Convert a string such that it can be used in a filename.

    Args:
        xs: String to convert.

    Returns:
        String usable for file name.
    """
    # Encode to ASCII.
    xs = xs.encode('ascii', 'ignore')

    # Convert characters.
    convert = {':': ',',
               ';': ','}
    for char_from, char_to in convert.items():
        xs = xs.replace(char_from, char_to)

    # Finally, whitelist characters.
    allowed = uppercase + lowercase + digits + '- !()-_=+\'",.'
    return filter(lambda x: x in allowed, xs)


class Encoder(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def encode(self, obj):
        pass

    @abc.abstractmethod
    def decode(self, obj):
        pass

    def compose(self, other):
        return ComposedEncoder(self, other)


class IdentityEncoder(Encoder):
    def encode(self, obj):
        return obj

    def decode(self, obj):
        return obj


class ComposedEncoder(Encoder):
    def __init__(self, *encoders):
        self.encoders = encoders

    def encode(self, obj):
        for encoder in reversed(self.encoders):
            obj = encoder.encode(obj)
        return obj

    def decode(self, obj):
        for encoder in self.encoders:
            obj = encoder.decode(obj)
        return obj


class Peekable(object):
    def __init__(self, obj):
        self.obj = obj

    def next(self):
        if len(self.obj) == 0:
            raise StopIteration
        else:
            current = self.obj[0]
            self.obj = self.obj[1:]
        return current

    def __iter__(self):
        return self

    def peek(self, num=1, start=0):
        return self.obj[start:start + num]

    def skip(self, num=1):
        self.obj = self.obj[num:]


class StringEncoder(Encoder):
    # TODO: Ensure that uppercase words and a certain list of words are braced.

    tex_mod_map = {'\'': u'\u0301',
                   '~': u'\u0303',
                   '`': u'\u0300',
                   '"': u'\u0308'}
    mod_map = {v: k for k, v in tex_mod_map.items()}
    ensure_braces = ['Gaussian', 'GP']

    def encode(self, obj):
        # Convert hard-coded LaTeX spaces to normal ones. BiBTeX should be able
        # to handle spaces correctly.
        obj = re.sub(r'^\\~', r' ', obj)  # The tildes should not be escaped.

        # Convert LaTeX-coded special character to their unicode variants.
        it = Peekable(obj)
        out = u''
        for x in it:
            if x == '{':
                if re.match(r'^\\[^a-zA-Z][a-zA-Z]\}$', it.peek(4)):
                    modifier = it.peek(start=1)
                    letter = it.peek(start=2)
                    if modifier not in StringEncoder.tex_mod_map:
                        raise RuntimeError('Cannot map modifier "{}".'
                                           ''.format(modifier))
                    it.skip(4)
                    out += letter + StringEncoder.tex_mod_map[modifier]
                    continue
            out += x

        # Finally, remove any LaTeX braces.
        out = out.replace('{', '').replace('}', '')
        return out

    def decode(self, obj):
        it = Peekable(unicodedata.normalize('NFD', obj))
        out = ''
        for x in it:
            if ord(x) < 128:
                out += x.encode('ascii')
            elif x in StringEncoder.mod_map:
                letter = out[-1]
                modifier = StringEncoder.mod_map[x]
                out = out[:-1] + '{{\\{}{}}}'.format(modifier, letter)
            else:
                raise RuntimeError('Cannot translate unicode ordinal {}.'
                                   ''.format(ord(x)))
        return out


class AuthorEncoder(Encoder):
    def encode(self, obj):
        authors = re.split(r'\sand\s', obj)

        # Remove commas.
        authors = [' '.join(reversed(author.split(','))) for author in authors]

        # Separate names. Properly take care of dots and dashes.
        # TODO: Preserve dashes in e.g. "Henk H.-V.".
        authors = [re.split('\.?-? ?', author) for author in authors]
        authors = [filter(None, map(lambda x: x.strip(), author))
                   for author in authors]

        # Add dots to single-letter names.
        authors = [[x + '.' if len(x) == 1 else x for x in author]
                   for author in authors]

        # Join names.
        authors = [' '.join(author) for author in authors]

        return authors

    def decode(self, obj):
        return ' and '.join(obj)


class TitleEncoder(Encoder):
    def encode(self, xs):
        def callback(x, all_caps):
            # This callback enforces uppercase words to remain uppercase.
            return x if x == x.upper() else None

        # TODO: Make titlecase not touch braces.
        return titlecase(xs, callback=callback)

    def decode(self, obj):
        return obj


class IntEncoder(Encoder):
    def encode(self, obj):
        # TODO: handle long forms
        return int(obj)

    def decode(self, obj):
        return str(obj)


class PagesEncoder(Encoder):
    def encode(self, obj):
        res_double = re.match(r'^([0-9]+)\-+([0-9]+)$', obj)
        res_single = re.match(r'^([0-9]+)$', obj)
        if res_double:
            return map(int, res_double.groups())
        elif res_single:
            warnings.warn('Pages encoded by a single digit.')
            return map(int, res_single.groups())
        else:
            raise RuntimeError('Could not parse pages "{}".'.format(obj))

    def decode(self, obj):
        if len(obj) == 1:
            return str(obj[0])
        elif len(obj) == 2:
            return '{}--{}'.format(*obj)
        else:
            raise RuntimeError('Unknown encode for pages: "{}".'.format(obj))


class MonthEncoder(Encoder):
    specs = [[datetime.date(2008, i, 1).strftime('%B') for i in range(1, 13)],
             [datetime.date(2008, i, 1).strftime('%b') for i in range(1, 13)],
             range(1, 13)]

    def encode(self, obj):
        for spec in MonthEncoder.specs:
            hits = [str(month).lower() in str(obj).lower() for month in spec]
            if sum(hits) == 1:
                return MonthEncoder.specs[0][hits.index(True)]
        raise RuntimeError('Could not decode month "{}".'.format(obj))

    def decode(self, obj):
        return obj


class ArXivEPrintEncoder(Encoder):
    def encode(self, obj):
        res = re.search(r'(abs\/)?([a-zA-Z\-]*\/?[0-9\.]+)$', obj)
        if res:
            return res.groups()[-1]
        else:
            raise RuntimeError('Could not decode arXiv identifier '
                               '"{}".'.format(obj))

    def decode(self, obj):
        return 'https://arxiv.org/abs/{}'.format(obj)


title_encoder = TitleEncoder().compose(StringEncoder())
author_encoder = AuthorEncoder().compose(StringEncoder())
encoders = {'author': author_encoder,
            'editor': author_encoder,
            'series': title_encoder,
            'month': MonthEncoder(),
            'title': title_encoder,
            'booktitle': title_encoder,
            'journal': title_encoder,
            'publisher': StringEncoder(),
            'school': StringEncoder(),
            'pages': PagesEncoder(),
            'volume': IntEncoder(),
            'number': IntEncoder(),
            'year': IntEncoder(),
            'edition': IntEncoder(),
            'chapter': IntEncoder(),
            'eprint': ArXivEPrintEncoder(),
            'url': IdentityEncoder()}


def encode(xs, generate_ids=False):
    """
    Encode a string containing BiBTeX entries, or re-encode previously
    encoded entries.

    TODO: Handle bug in BP: ensure comma after final field.

    Args:
        xs: String containing BiBTeX entries.
        generate_ids (bool, optional): Overwrite the IDs.

    Returns:
        BiBTeX entries represented as a dictionaries.
    """
    # Parse entries and determine their IDs.
    if isinstance(xs, str):
        parsed_entries = bp.loads(xs).entries
        parsed_ids = [x['ID'] for x in parsed_entries]
    elif isinstance(xs, list):
        parsed_entries = [x['raw'] for x in xs]
        # Preserve previously generated IDs.
        parsed_ids = [x['ID'] for x in xs]
    else:
        raise ValueError('Unknown type "{}" for input.'.format(type(xs)))

    # Encode the entries.
    entries = [{k: encoders[k].encode(v)
                for k, v in map(lambda (k, v): (k.lower()
                                                .encode('ascii'), v),
                                entry.items())
                if k in encoders}
               for entry in parsed_entries]

    # Process special properties.
    for entry, parsed_entry, parsed_id in zip(entries, parsed_entries,
                                              parsed_ids):
        entry['type'] = parsed_entry['ENTRYTYPE']
        entry['id'] = parsed_id
        entry['raw'] = parsed_entry

        # Generate an ID for the entry if required.
        if generate_ids:
            # Generate the three parts: author, year, and title.
            first_author = entry['author'][0]
            author = first_author.split()[-1].encode('ascii', 'ignore')
            year = str(entry['year'])
            title_parts = entry['title'].split()[:5]
            title = '_'.join(title_parts).encode('ascii', 'ignore')

            # Filter characters.
            allowed = uppercase + lowercase + digits + '-_'
            author, title = map(lambda xs: filter(lambda x: x in allowed, xs),
                                (author, title))

            # Combine the parts into the ID.
            entry['id'] = '{}:{}:{}'.format(author, year, title)

    return entries


def decode(obj):
    """
    Decode an encoded BiBTeX string.

    Args:
        obj: Encoding.

    Returns:
        BiBTeX string.
    """
    decoded_entries = [{k: encoders[k].decode(v)
                        for k, v in decoded_entry.items()
                        if k in encoders}
                       for decoded_entry in obj]
    out = ''
    for decoded_entry, enty in zip(decoded_entries, obj):
        content = '\n'.join(['    {key} = {{{value}}},'.format(key=k, value=v)
                             for k, v in decoded_entry.items()])
        out += '@{type}{{{id},\n{content}\n}}\n\n' \
               ''.format(type=enty['type'],
                         id=enty['id'],
                         content=content)
    return out


def get_last_name(name):
    """
    Get the last name.

    Args:
        name: Full name.

    Returns:
        Last name.
    """
    names = name.split(' ')
    last_name_reversed = [names[-1]]

    # Get all tussenvoegsels.
    for name in reversed(names[:-1]):
        # If it starts with a lower letter, then it is a tussenvoegsel.
        if name[0] == name[0].lower():
            last_name_reversed.append(name)
        else:
            break

    return ' '.join(reversed(last_name_reversed))


def generate_file_name(entry):
    """
    Generate the file name for an entry.

    Args:
        entry: Entry.

    Returns:
        File name.
    """
    return str_for_file(u'{name}, {year}, {title}'.format(
        year=entry['year'],
        name=get_last_name(entry['author'][0]),
        title=entry['title']
    ))
