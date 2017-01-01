config = {
    # Path to resources
    'resource_path': '/Users/Wessel/Dropbox/Resources',

    # Path to this repository
    'catalogue_path': '/Users/Wessel/Dropbox/Projects/Development/Catalogue',

    # Prefix to remove from displayed paths
    'base_path': '/Users/Wessel/Dropbox',

    # System binaries
    'binaries': {'find': '/usr/bin/find',
                 'mdfind': '/usr/bin/mdfind',
                 'fzf': '/usr/local/bin/fzf',
                 'subl': '/usr/local/bin/subl',
                 'pbpaste': '/usr/bin/pbpaste',
                 'trash': '/usr/local/bin/trash'}
}

# Bib config
names = [
    'Gaussian',
    'Copula',
    'Atari',
    'Toeplitz'
]

replacements = [
    ('1st', 'first'),
    ('2nd', 'second'),
    ('3rd', 'third'),
    ('4th', 'fourth'),
    ('5th', 'fifth'),
    ('6th', 'sixth'),
    ('7th', 'seventh'),
    ('8th', 'eighth'),
    ('9th', 'ninth'),
    ('10th', 'tenth'),
    ('11th', 'eleventh'),
    ('12th', 'twelfth'),
    ('13th', 'thirteenth'),
    ('14th', 'fourteenth'),
    ('15th', 'fifteenth'),
    ('16th', 'sixteenth'),
    ('17th', 'seventeenth'),
    ('18th', 'eighteenth'),
    ('19th', 'nineteenth'),
    ('20th', 'twentieth'),
    ('&', '\\&'),
    ('Alvarez', "{\\'A}lvarez")
]

allowed_keys = [
    'address',
    'annote',
    'author',
    'booktitle',
    'chapter',
    'crossref',
    'edition',
    'howpublished',
    'institution',
    'journal',
    'month',
    'note',
    'number',
    'organization',
    'pages',
    'publisher',
    'school',
    'series',
    'title',
    'volume',
    'year',

    'eprint',
    'id',
    'link',
    'url'
]
