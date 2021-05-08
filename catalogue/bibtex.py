import abc
import datetime
import re
import unicodedata
import warnings
from string import ascii_uppercase as uppercase, ascii_lowercase as lowercase, digits
from subprocess import Popen, PIPE

import bibtexparser as bp
import feedparser
from plum import Dispatcher
from titlecase import titlecase

from config import config

__all__ = ["generate_file_name", "is_arxiv", "fetch_arxiv", "encode", "decode"]

_dispatch = Dispatcher()


def get_last_name(name):
    """Get the last name.

    Args:
        name (str): Full name.

    Returns:
        str: Last name.
    """
    names = name.split(" ")
    last_name_reversed = [names[-1]]

    # Get all tussenvoegsels.
    for name in reversed(names[:-1]):
        # If it starts with a lower letter, then it is a tussenvoegsel.
        if name[0] == name[0].lower():
            last_name_reversed.append(name)
        else:
            break

    return " ".join(reversed(last_name_reversed))


def generate_file_name(entry):
    """Generate the file name for an entry.

    Args:
        entry (dict): Entry.

    Returns:
        str: File name.
    """
    return str_for_file(
        "{name}, {year}, {title}".format(
            year=entry["year"],
            name=get_last_name(entry["author"][0]),
            title=entry["title"],
        )
    )


def generate_id(entry):
    """Generate an ID for an entry.

    Args:
        entry (dict): Entry.

    Returns:
        str: ID.
    """
    # Generate the three parts: author, year, and title.
    first_author = entry["author"][0]
    author = unicode_to_ascii(first_author.split()[-1])
    year = str(entry["year"])
    title_parts = entry["title"].split()[:5]
    title = unicode_to_ascii("_".join(title_parts))

    # Filter characters.
    allowed = uppercase + lowercase + digits + "-_"
    author = "".join(filter(lambda x: x in allowed, author))
    title = "".join(filter(lambda x: x in allowed, title))

    # Combine the parts into the ID.
    return "{}:{}:{}".format(author, year, title)


replacements = {"\xE5": "a", "\u212B": "A", "\u00e6": "ae"}


def unicode_to_ascii(x):
    """Convert a unicode string to ASCII, cleverly replacing characters.

    Args:
        x (str): Unicode string.

    Returns:
        str: `x` as ASCII.
    """
    for key, value in replacements.items():
        x = x.replace(key, value)
    return x.encode("ascii", "ignore").decode()


def is_arxiv(fp):
    """Check whether a PDF is from arXiv.

    Args:
        fp (str): File path.

    Returns:
        tuple[str, str]: The detected arXiv category and identifier if
            the PDF if from arXiv and `None` otherwise.

    """
    # Attempt to extract the arXiv number via `pdfgrep`.
    process = Popen(
        [config["binaries"]["pdfgrep"], "-m", "1", "-h", "arXiv", fp], stdout=PIPE
    )
    out = process.communicate()[0].decode().strip()
    res = re.match(
        r"arXiv:([a-zA-Z\-]*)\/?([0-9\.]+)v([0-9]+) " r"\[?([0-9a-zA-Z. _\-]+)\]?", out
    )
    if res:
        cat, num, _, _ = res.groups()
        return cat, num
    return None


def str_for_file(xs):
    """Convert a string such that it can be used in a filename.

    Args:
        xs: String to convert.

    Returns:
        String usable for file name.
    """
    # Encode to ASCII.
    xs = unicode_to_ascii(xs)

    # Convert characters.
    convert = {":": ",", ";": ","}
    for char_from, char_to in convert.items():
        xs = xs.replace(char_from, char_to)

    # Finally, whitelist characters.
    allowed = uppercase + lowercase + digits + "- !()-_=+'\",."
    return "".join(filter(lambda x: x in allowed, xs))


def fetch_arxiv(fp, info=None):
    """Fetch the BiBTeX for an arXiv PDF.

    Args:
        fp: Path.
        info (optional): arXiv info from :method:`.bibtex.is_arxiv`.

    Returns:
        list[dict]: The BiBTeX if it can be found and `None` otherwise.
    """
    info = info if info else is_arxiv(fp)

    if info:
        cat, num = info
        feed = feedparser.parse(
            f"https://export.arxiv.org/api/query?search_query=all:{num}"
        )

        # Check that results is not ambiguous.
        num_results = len(feed["entries"])
        if num_results != 1:
            raise RuntimeError(
                f"Query not unambiguous: found {num_results} results."
            )

        # Construct raw content of entry.
        entry = feed["entries"][0]
        year, month = map(int, entry["published"].split("-")[:2])
        entry = {
            "type": "article",
            "title": entry["title"],
            "author": " and ".join([x["name"] for x in entry["authors"]]),
            "year": year,
            "month": month,
            "eprint": num,
            "journal": "arXiv E-Prints",
        }
        return [entry]
    else:
        return None


class Encoder(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def encode(self, obj):
        pass

    @abc.abstractmethod
    def decode(self, obj, entry):
        pass

    def compose(self, other):
        return ComposedEncoder(self, other)


class IdentityEncoder(Encoder):
    def encode(self, obj):
        return obj

    def decode(self, obj, entry):
        return obj


class ComposedEncoder(Encoder):
    def __init__(self, *encoders):
        self.encoders = encoders

    def encode(self, obj):
        for encoder in reversed(self.encoders):
            obj = encoder.encode(obj)
        return obj

    def decode(self, obj, entry):
        for encoder in self.encoders:
            obj = encoder.decode(obj, entry)
            if obj is None:
                return None
        return obj


class Peekable(object):
    def __init__(self, obj):
        self.obj = obj

    def __next__(self):
        if len(self.obj) == 0:
            raise StopIteration
        else:
            current = self.obj[0]
            self.obj = self.obj[1:]
        return current

    def next(self):
        return self.__next__()

    def __iter__(self):
        return self

    def peek(self, num=1, start=0):
        return self.obj[start : start + num]

    def skip(self, num=1):
        self.obj = self.obj[num:]


class StringEncoder(Encoder):
    # TODO: Ensure that uppercase words and a certain list of words are braced.

    tex_mod_map = {
        "'": "\u0301",
        "^": "\u0302",
        "~": "\u0303",
        "`": "\u0300",
        '"': "\u0308",
        "v": "\u030c",
        "r": "\u030A",
        "c": "\u0327",
        "k": "\u0328",
    }
    mod_map = {v: k for k, v in tex_mod_map.items()}
    tex_commands = {
        "O": "\xD8",
        "o": "\xF8",
        "aa": "\xE5",
        "ae": "\u00e6",
        "AA": "\u212B",
    }
    commands = {v: k for k, v in tex_commands.items()}

    def encode(self, obj):
        # Convert hard-coded LaTeX spaces to normal ones. BiBTeX should be able
        # to handle spaces correctly.
        obj = re.sub(r"([^\\])~", r"\1 ", obj)
        obj = re.sub(r"^~", " ", obj)

        # Replace LaTeX commands.
        for command, result in StringEncoder.tex_commands.items():
            obj = re.sub(r"\\" + command + r"([^a-zA-Z])", result + r"\1", obj)
            obj = re.sub(r"\\" + command + r"$", result, obj)

        # Convert LaTeX-coded special character to their unicode variants.
        it = Peekable(obj)
        out = ""
        for x in it:
            if x == "\\":
                res = re.match(r"^(.) *\{?([a-zA-Z])\}?", it.peek(10))
                if res:
                    # Get the letters and modifier.
                    modifier = res.groups()[0]
                    letter = res.groups()[1]

                    if modifier not in StringEncoder.tex_mod_map:
                        raise RuntimeError(
                            "StringEncoder: cannot map "
                            'modifier "{}".'.format(modifier)
                        )

                    # Skip.
                    it.skip(res.span()[1])

                    out += letter + StringEncoder.tex_mod_map[modifier]
                    continue

            out += x

        # Finally, remove any LaTeX braces.
        out = out.replace("{", "").replace("}", "")
        return out

    def decode(self, obj, entry):
        it = Peekable(unicodedata.normalize("NFD", obj))
        out = ""
        for x in it:
            if ord(x) < 128:
                out += x.encode("ascii").decode()
            elif x in StringEncoder.mod_map:
                letter = out[-1]
                modifier = StringEncoder.mod_map[x]
                out = out[:-1] + "{{\\{} {}}}".format(modifier, letter)
            elif x in StringEncoder.commands:
                out += "{{\\{}}}".format(StringEncoder.commands[x])
            else:
                raise RuntimeError(
                    "StringEncoder: cannot translate unicode "
                    "ordinal {}.".format(ord(x))
                )
        return out


class AuthorEncoder(Encoder):
    name_combiners = "-"

    def encode(self, obj):
        # Split authors.
        authors = re.split(r"\sand\s", obj)

        # Remove commas.
        authors = [" ".join(reversed(author.split(","))) for author in authors]

        # Separate names. This splits off combined names, e.g. "H.-V." becomes
        # "H -V". We'll join them afterwards.
        def separate(author):
            # First split off combined names.
            for x in AuthorEncoder.name_combiners:
                author = author.replace(x, " " + x)

            # Split.
            author = re.split("[. ]", author)

            # Filter and return
            return filter(None, [x.strip() for x in author])

        authors = [separate(author) for author in authors]

        # Add dots to single-letter names.
        authors = [
            [x + "." if self._is_single_letter(x) else x for x in author]
            for author in authors
        ]

        # Join names. Combined names are still split off.
        authors = [" ".join(author) for author in authors]

        # Join split-off combined names.
        def combine(author):
            for x in AuthorEncoder.name_combiners:
                author = author.replace(" " + x, x)
            return author

        authors = [combine(author) for author in authors]

        return authors

    def _is_single_letter(self, x):
        if x[0] in AuthorEncoder.name_combiners:
            return self._is_single_letter(x[1:])
        else:
            return len(x) == 1

    def decode(self, obj, entry):
        return " and ".join(obj)


class TitleEncoder(Encoder):
    _protected = [
        "Bayes",
        "Bernstein",
        "Canadian",
        "Chernoff",
        "Cholesky",
        "Cox",
        "Fisher" "Fokker",
        "GP",
        "Gibbs",
        "Gauss",
        "Hilbert",
        "Hoeffding",
        "Hormander",  # TODO: Make insensitive to unicode.
        "Kalman",
        "Kronecker",
        "Krylov",
        "Jaynes",
        "Jaynesian",
        "Kullback",
        "Langevin",
        "Leibler",
        "Mahalanobis",
        "Newton",
        "ODE",
        "PAC",
        "PDE",
        "Planck",
        "Renyi",
        "SPDE",
        "Sinkhorn",
        "Stein",
        "Sylvester",
        "Tietze",
        "VampPrior",
        "Volterra",
        "Wasserstein",
    ]

    def encode(self, xs):
        def callback(x, all_caps):
            # This callback enforces uppercase words to remain uppercase.
            if x == x.upper():
                return x
            elif len(x) > 1 and x[-1] == "s" and x[:-1] == x[:-1].upper():
                return x
            else:
                return None

        # TODO: Make titlecase not touch braces.
        return titlecase(xs, callback=callback)

    def decode(self, obj, entry):
        def process(word):
            # Test that it isn't math.
            if len(word) > 2 and word[0] == "$" and word[-1] == "$":
                return "{" + word + "}"

            # Test that capitalisation actually matters:
            if word == word.upper() and word == word.lower():
                return word

            # TODO: deal with false positives

            # Check whether it contains a protected word.
            protected = any([word.startswith(x) for x in TitleEncoder._protected])
            if (
                word == word.upper()
                or (
                    len(word) > 1 and word[-1] == "s" and word[:-1] == word[:-1].upper()
                )
                or protected
            ):
                return "{" + word + "}"
            else:
                return word

        return _split_map_join(process, [obj], [" ", "/", "-", ":", "."])[0]


def _split_map_join(f, xs, splitters):
    if len(splitters) == 0:
        return map(f, xs)
    else:
        s, splitters = splitters[0], splitters[1:]
        return [s.join(_split_map_join(f, x.split(s), splitters)) for x in xs]


class IntEncoder(Encoder):
    def encode(self, obj):
        # TODO: Handle long forms.
        return int(obj)

    def decode(self, obj, entry):
        return str(obj)


class PagesEncoder(Encoder):
    def encode(self, obj):
        # First strip spaces.
        obj = obj.replace(" ", "")

        # Then match.
        res_double = re.match(r"^([0-9]+)\-+([0-9]+)$", obj)
        res_single = re.match(r"^([0-9]+)$", obj)
        if res_double:
            return [int(x) for x in res_double.groups()]
        elif res_single:
            warnings.warn("Pages encoded by a single digit.")
            return [int(x) for x in res_single.groups()]
        else:
            raise RuntimeError('Could not parse pages "{}".'.format(obj))

    def decode(self, obj, entry):
        if len(obj) == 1:
            return str(obj[0])
        elif len(obj) == 2:
            return "{}--{}".format(*obj)
        else:
            raise RuntimeError('Unknown encode for pages: "{}".'.format(obj))


class MonthEncoder(Encoder):
    specs = [
        range(1, 13),
        [datetime.date(2008, i, 1).strftime("%B") for i in range(1, 13)],
        [datetime.date(2008, i, 1).strftime("%b") for i in range(1, 13)],
        [datetime.date(2008, i, 1).strftime("%b").lower() for i in range(1, 13)],
    ]

    def encode(self, obj):
        return MonthEncoder.specs[0][self._match(obj)]

    def decode(self, obj, entry):
        return MonthEncoder.specs[2][self._match(obj)]

    def _match(self, obj):
        for spec in MonthEncoder.specs:
            # Test for exact hits.
            hits = [str(month).lower() == str(obj).lower() for month in spec]
            if sum(hits) == 1:
                return hits.index(True)

            # Test for contained hits.
            hits = [str(month).lower() in str(obj).lower() for month in spec]
            if sum(hits) == 1:
                return hits.index(True)
        raise RuntimeError('Could not match month "{}".'.format(obj))


class ArXivEPrintEncoder(Encoder):
    def encode(self, obj):
        res = re.search(r"(abs\/)?([a-zA-Z\-]*\/?[0-9\.]+)$", obj)
        if res:
            return res.groups()[-1]
        else:
            raise RuntimeError("Could not decode arXiv identifier " '"{}".'.format(obj))

    def decode(self, obj, entry):
        return "https://arxiv.org/abs/{}".format(obj)


class ArXivFilter(Encoder):
    def encode(self, obj):
        return obj

    def decode(self, obj, entry):
        if "arxiv" in obj.lower():
            if "eprint" in entry:
                return "arXiv preprint arXiv:{}".format(entry["eprint"])
            else:
                return "arXiv preprint"
        else:
            return obj


class DOIEncoder(Encoder):
    def encode(self, obj):
        res = re.match(
            r"^(https?://)?(www\.)?(doi\.org/)?(.*)$", obj, flags=re.IGNORECASE
        )
        if res:
            return res.groups()[-1]
        else:
            raise RuntimeError('Could not decode DOI "{}".'.format(obj))

    def decode(self, obj, entry):
        return obj


title_encoder = TitleEncoder().compose(StringEncoder())
author_encoder = AuthorEncoder().compose(StringEncoder())
encoders = {
    "author": author_encoder,
    "editor": author_encoder,
    "series": title_encoder,
    "month": MonthEncoder(),
    "title": title_encoder,
    "booktitle": ArXivFilter().compose(title_encoder),
    "booksubtitle": title_encoder,
    "maintitle": title_encoder,
    "journal": ArXivFilter().compose(title_encoder),
    "publisher": StringEncoder(),
    "school": StringEncoder(),
    "institution": StringEncoder(),
    "pages": PagesEncoder(),
    "volume": IntEncoder(),
    "number": IntEncoder(),
    "year": IntEncoder(),
    "edition": IntEncoder(),
    "chapter": IntEncoder(),
    "eprint": ArXivEPrintEncoder(),
    "url": IdentityEncoder(),
    "pdf": IdentityEncoder(),
    "note": IdentityEncoder(),
    "urldate": IdentityEncoder(),
    "doi": DOIEncoder(),
    "issn": IdentityEncoder(),
    "crossref": IdentityEncoder(),
}


@_dispatch
def encode(xs: list, generate_ids=False):
    """Encode a string containing BiBTeX entries, a list of dictionaries which
    represent the parsed BiBTeX, or a list of encoded entries with a raw
    dictionary representation available.

    TODO: Handle bug in BP: ensure comma after final field.

    Args:
        xs (str or list): BiBTeX entries.
        generate_ids (bool, optional): Overwrite the IDs.

    Returns:
        BiBTeX entries represented as a dictionaries.
    """
    # Extract raw where possible.
    parsed_entries = [x["raw"] if "raw" in x else x for x in xs]

    # Encode the entries, skipping those where the decoding fails.
    encoded_entries = []
    for entry in parsed_entries:
        encoded_entry = {}
        for k, v in entry.items():
            if k in encoders:
                try:
                    encoded_entry[k] = encoders[k].encode(v)
                except RuntimeError:
                    # Could not encode entry. Skip it.
                    continue
        encoded_entries.append(encoded_entry)

    # Process special fields.
    for encoded_entry, parsed_entry in zip(encoded_entries, parsed_entries):
        encoded_entry["type"] = parsed_entry["type"].lower()
        encoded_entry["raw"] = parsed_entry

        # Generate an ID for the entry if required.
        if generate_ids:
            encoded_entry["id"] = generate_id(encoded_entry)

    return encoded_entries


@_dispatch
def encode(xs: str, generate_ids=False):
    parser = bp.bparser.BibTexParser(common_strings=True, homogenize_fields=True)
    entries = bp.loads(xs, parser).entries

    # Standardise keys in parsed entries.
    entries = [
        {k.encode("ascii").decode().lower(): v for k, v in entry.items()}
        for entry in entries
    ]

    # Fix up entries.
    for entry in entries:
        # Rename `entrytype` to `type`.
        entry["type"] = entry["entrytype"]
        del entry["entrytype"]

    return encode(entries, generate_ids=generate_ids)


def decode(obj):
    """Decode an encoded BiBTeX string.

    Args:
        obj (object): Encoding.

    Returns:
        str: BiBTeX string.
    """
    # Move crossreferences to end.
    obj = [entry for entry in obj if entry["type"].lower() != "proceedings"] + [
        entry for entry in obj if entry["type"].lower() == "proceedings"
    ]

    # Decode the entries.
    decoded_entries = []
    for decoded_entry in obj:
        entry = {}
        for k, v in decoded_entry.items():
            if k in encoders:
                res = encoders[k].decode(v, decoded_entry)

                # Only add the result if is it not `None`.
                if res is not None:
                    entry[k] = res

        # Check whether `crossref` in included, but `type` isn't appropriate.
        if "crossref" in entry and not decoded_entry["type"].lower().startswith("in"):
            warnings.warn(
                'For ID "{}" with title "{}", a cross-reference is '
                'used, but the type is "{}".'
                "".format(decoded_entry["id"], entry["title"], decoded_entry["type"])
            )

        decoded_entries.append(entry)

    # Convert to text, minding duplicate entries.
    out, processed_ids = "", []
    for decoded_entry, entry in zip(decoded_entries, obj):
        # Check whether the entry has already been converted to text.
        if entry["id"].lower() in processed_ids:
            continue
        else:
            processed_ids.append(entry["id"].lower())

        # Convert to text.
        content = "\n".join(
            [
                "    {key} = {{{value}}},".format(key=k, value=v)
                for k, v in decoded_entry.items()
            ]
        )
        out += "@{type}{{{id},\n{content}\n}}\n\n" "".format(
            type=entry["type"], id=entry["id"], content=content
        )
    return out
