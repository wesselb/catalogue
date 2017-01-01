from titlecase import titlecase
from string import lowercase, uppercase
import config
import json
import textwrap
import re


def is_numeric(value):
    """
    Check whether a value is numeric, ignoring ordinal indicators.
    :param value: value
    :return: boolean whether value is numeric
    """
    try:
        to_numeric(value)
        return True
    except ValueError:
        return False


def to_numeric(value):
    """
    Convert a value to a number, ignoring ordinal indicators.
    :param value: value
    :return: converted value
    """
    return int(StringNormaliser.filter(value))


def purge_list(xs):
    """
    Purge a list of strings by stripping all elements and removing empty
    elements.
    :param xs: list
    :return: purged list
    """
    xs = map(lambda x: x.strip(), xs)
    return filter(None, xs)


def remove_ordinal_indicators(value):
    """
    Convert a value to lower case and remove ordinal indicators.
    :param value: value
    :return: converted value
    """
    indicators = ['th', 'nd', 'rd', 'st']
    value = value.lower()
    for indicator in indicators:
        value = value.replace(indicator, '')
    return value.strip()


def top_split(value, delimiter=','):
    """
    Split a string by a delimiter. Don't split when the delimiter is inside
    curly braces, single quotes, or double quotes.
    :param value: value to split
    :param delimiter: delimiter
    :return: splitted value
    """
    splitted = ['']
    curly_level = 0
    in_double = False
    in_single = False
    iterator = iter(value)
    for character in iterator:
        # Check for escaping
        if character == '\\' and (in_single or in_double or curly_level > 0):
            splitted[-1] += character + next(iterator)
        else:
            # Process braces and quotes
            if character == '{':
                curly_level += 1
            elif character == '}':
                curly_level -= 1
            elif character == '\'' and not in_double:
                in_single = not in_single
            elif character == '"' and not in_single:
                in_double = not in_double
            # Process character
            if character == delimiter \
                    and curly_level == 0 \
                    and not in_double \
                    and not in_single:
                splitted += ['']
            else:
                splitted[-1] += character
    return splitted


def compose(*funs):
    """
    Compose functions.
    :param funs: functions
    :return: composition of functions
    """
    def composed_fun(*args, **kw_args):
        value = funs[-1](*args, **kw_args)
        for fun in reversed(funs[0:-1]):
            value = fun(value)
        return value
    return composed_fun


class StringNormaliser:
    """
    Normalise a string.
    """

    @staticmethod
    def filter(value):
        """
        Normalise a string.
        :param value: string to normalise
        :return: normalised string
        """
        return compose(StringNormaliser._brace_names,
                       StringNormaliser._brace_abbrevs,
                       StringNormaliser._apply_replacements,
                       StringNormaliser._filter_string)(value)

    @staticmethod
    def _filter_string(value):
        """ Filter a string. """
        # Remove braces
        value = filter(lambda x: x != '{' and x != '}', value)
        # Remove LaTeX commands
        value = re.sub(r'(\\[a-zA-Z]+|\\[\^~\'"=.`])', '', value)
        # Convert hard spaces
        value = value.replace('~', ' ')
        return value

    @staticmethod
    def _apply_replacements(value):
        """ Apply defined replacements to a string. """
        for original, replacement in config.replacements:
            value = value.replace(original, replacement)
        return value

    @staticmethod
    def _brace_names(value, names=config.names):
        """ Brace names. """
        for name in names:
            value = value.replace(name, '{' + name + '}')
        return value

    @staticmethod
    def _brace_abbrevs(value):
        """ Brace abbreviations. """
        words = re.findall('[a-zA-Z]+', value)
        # Any word with an uppercase letter not in the first position is a name
        names = filter(lambda x: any(map(lambda y: y in uppercase, x[1:])),
                       words)
        return StringNormaliser._brace_names(value, names)


class BibParser:
    """
    Parse the content of a .bib file.
    :param content: Content of the .bib file
    """
    def __init__(self, content):
        entries = purge_list(content.split('@'))
        self._parsed_entries = []
        for entry in entries:
            self._parsed_entries.append(self._parse_entry(entry))

    def _parse_entry(self, entry):
        """ Parse a single entry. """
        parsed_entry = {}
        # Last character is always a '}', remove it
        entry = entry[:-2]
        # Extract type
        splitted_entry = purge_list(entry.split('{', 1))
        parsed_entry['type'] = splitted_entry[0].lower()
        # Extract further fields
        fields = purge_list(top_split(splitted_entry[1]))
        parsed_entry.update(self._parse_fields(fields))
        # Generate field 'id'
        return self._generate_id(parsed_entry)

    def _generate_id(self, entry):
        """ Generate the 'id' field for an entry. """
        # Generate title from first five words
        filtered_title = filter(lambda x: x in lowercase + uppercase + '_-',
                                '_'.join(entry['title'].split(' ')[:5]))
        # Take care of comma notation
        author = entry['author'][0].split(',')[0]
        author = author.strip().split(' ')[-1]
        # Format field 'id'
        entry['id'] = '{}:{}:{}'.format(author, entry['year'], filtered_title)
        return entry

    def _remove_enclosing(self, value):
        """ Remove enclosing characters. """
        value = value.strip()
        opening, closing = ['\'', '"', '{'], ['\'', '"', '}']
        while (value[0], value[-1]) in zip(opening, closing):
            value = value[1:-1].strip()
        return value

    def _parse_fields(self, fields):
        """ Parse a list of fields obtained from the BiBTeX source. """
        parsed_entry = {'id': fields[0]}
        for field in fields[1:]:
            splitted_field = field.split('=', 1)
            key = splitted_field[0].strip()
            if key not in config.allowed_keys:
                continue
            unparsed_value = self._remove_enclosing(splitted_field[1])
            parsed_entry[key] = self._parse_value(key, unparsed_value)
        return parsed_entry

    def _parse_value(self, key, value):
        """ Parse a value according to its key. """
        if is_numeric(value):
            return to_numeric(value)
        elif key == 'pages':
            num_dashes = sum(map(lambda x: x == '-', value))
            if num_dashes == 0:
                return int(value)
            else:
                return map(int, value.split('-' * num_dashes))
        elif key == 'author':
            return purge_list(StringNormaliser.filter(value).split(' and '))
        elif key == 'journal' or key == 'booktitle' or key == 'title':
            return titlecase(StringNormaliser.filter(value))
        elif key == 'link':
            return value
        else:
            return StringNormaliser.filter(value)

    def to_json(self):
        """
        Convert parsed BiBTeX to JSON.
        :return: JSON
        """
        return json.dumps(self._parsed_entries, indent=4, sort_keys=True)


class BibRenderer:
    """
    Render a BiBTeX file from interpreted JSON source.
    :param entries: entries in the JSON file
    """
    _template_entry = textwrap.dedent('''
    @{type:s}{{{id:s},
        {fields:s}
    }}
    ''')

    def __init__(self, entries):
        self._entries = entries

    def as_text(self):
        """
        Output BiBTeX source.
        :return: BiBTeX source
        """
        return '\n'.join(map(self._entry_to_text, self._entries))

    def _entry_to_text(self, entry):
        """ Convert an entry to text. """
        entry = dict(entry)
        entry_type, entry_id = entry['type'], entry['id']
        del entry['type']
        del entry['id']
        fields = map(lambda (k, v): ''.join([k, ' = ',  '{',
                                             self._value_to_text(k, v), '}']),
                     entry.items())
        return self._template_entry.format(type=entry_type,
                                           id=entry_id,
                                           fields=',\n    '.join(fields))

    def _value_to_text(self, key, value):
        """ Convert a value to text. """
        if type(value) == str or type(value) == unicode:
            return StringNormaliser.filter(str(value.encode('ascii', 'ignore')))
        elif type(value) == int:
            return str(value)
        elif key == 'author':
            return StringNormaliser.filter(' and '.join(value))
        elif key == 'pages':
            return '--'.join(map(str, value))
        else:
            raise ValueError('Key \'{}\' cannot be matched with value \'{}\''
                             .format(key, value))
