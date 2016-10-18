from titlecase import titlecase
from string import lowercase, uppercase
from config import names, replacements
import json
import textwrap


def is_numeric(value):
    """ Check whether a value is numeric, ignoring ordinal indicators. """
    try:
        to_numeric(value)
        return True
    except ValueError:
        return False


def to_numeric(value):
    """ Convert a value to a number, ignoring ordinal indicators. """
    return int(StringFilter.filter(value))


def purge(xs):
    """
    Purge a list of strings by stripping all elements and removing empty
    elements.
    """
    xs = map(lambda x: x.strip(), xs)
    return filter(None, xs)


def remove_ordinal_indicators(value):
    """ Convert a value to lower case and remove ordinal indicators. """
    indicators = ['th', 'nd', 'rd', 'st']
    value = value.lower()
    for indicator in indicators:
        value = value.replace(indicator, '')
    return value.strip()


def top_split(value, delimiter=','):
    """
    Split a string by a delimiter.

    Specifically, don't split when
        - the delimiter is inside curly braces,
        - the delimiter is inside single quotes or
        - the delimiter is inside double quotes.

    :param value: Value to split
    :param delimiter: Delimiter
    :return: Splitted value
    """
    splitted = ['']
    curly_level = 0
    in_double = False
    in_single = False
    iterator = iter(value)
    for character in iterator:
        if character == '\\' and (in_single or in_double or curly_level > 0):
            splitted[-1] += character + next(iterator)
        else:
            if character == '{':
                curly_level += 1
            elif character == '}':
                curly_level -= 1
            elif character == '\'' and not in_double:
                in_single = not in_single
            elif character == '"' and not in_single:
                in_double = not in_double
            elif character == delimiter \
                    and curly_level == 0 \
                    and not in_double \
                    and not in_single:
                splitted += ['']
            else:
                splitted[-1] += character
    return splitted


def compose(*funs):
    def composed_fun(*args, **kw_args):
        value = funs[-1](*args, **kw_args)
        for fun in reversed(funs[0:-1]):
            value = fun(value)
        return value
    return composed_fun


class StringFilter:
    """
    Filter a string compliant with BibTeX syntax.
    """

    _allowed_letters = '& :,.0123456789-' + lowercase + uppercase

    @staticmethod
    def filter(value):
        return compose(StringFilter._brace_names,
                       StringFilter._apply_replacements,
                       StringFilter._filter_string)(value)

    @staticmethod
    def _filter_string(value):
        """ Filter a string by only allowing allowed characters. """
        return filter(lambda x: x in StringFilter._allowed_letters, value)

    @staticmethod
    def _apply_replacements(value):
        """ Apply the defined replacements to a string. """
        for original, replacement in replacements:
            value = value.replace(original, replacement)
        return value

    @staticmethod
    def _brace_names(value):
        """ Brace the defined names. """
        for name in names:
            value = value.replace(name, '{' + name + '}')
        return value


class BibParser:
    """
    Parse the content of a .bib file.

    :param content: Content of the .bib file
    """
    def __init__(self, content):
        entries = purge(content.split('@'))
        self._parsed_entries = []
        for entry in entries:
            self._parsed_entries.append(self._parse_entry(entry))

    def _parse_entry(self, entry):
        parsed_entry = {}
        # Last character should be '}', remove it
        entry = entry[:-2]
        splitted_entry = purge(entry.split('{', 1))
        parsed_entry['type'] = splitted_entry[0].lower()
        fields = purge(top_split(splitted_entry[1]))
        parsed_entry.update(self._parse_fields(fields))
        return parsed_entry

    def _remove_enclosing(self, value):
        value = value.strip()
        if value[0] in ['\'', '"', '{']:
            return value[1:-2]
        return value

    def _parse_fields(self, fields):
        parsed_entry = {}
        parsed_entry['id'] = fields[0]
        for field in fields[1:]:
            field = self._remove_enclosing(field)
            splitted_field = field.split('=', 1)
            key = splitted_field[0].strip()
            value = self._parse_value(key, splitted_field[1].strip())
            parsed_entry[key] = value
        return parsed_entry

    def _parse_value(self, key, value):
        if is_numeric(value):
            return to_numeric(value)
        elif key == 'pages':
            num_dashes = sum(map(lambda x: x == '-', value))
            if num_dashes == 0:
                return int(value)
            else:
                return map(int, value.split('-' * num_dashes))
        elif key == 'author':
            return purge(StringFilter.filter(value).split(' and '))
        elif key == 'journal' or key == 'booktitle' or key == 'title':
            return StringFilter.filter(titlecase(value))
        elif key == 'link':
            return value
        else:
            return StringFilter.filter(value)

    def to_json(self):
        return json.dumps(self._parsed_entries, indent=4, sort_keys=True)


class BibRenderer:
    _template_entry = textwrap.dedent('''
    @{type:s}{{{id:s},
        {fields:s}
    }}
    ''')

    def __init__(self, entries):
        self._entries = entries

    def as_text(self):
        return '\n'.join(map(self._entry_to_text, self._entries))

    def _entry_to_text(self, entry):
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
        if type(value) == str or type(value) == unicode:
            return StringFilter.filter(str(value.encode('ascii', 'ignore')))
        elif type(value) == int:
            return str(value)
        elif key == 'author':
            return StringFilter.filter(' and '.join(value))
        elif key == 'pages':
            return '--'.join(map(str, value))
        else:
            raise ValueError('Key \'{}\' cannot be matched with value \'{}\''
                             .format(key, value))
