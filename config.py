config = {
    'resource_path': '/Users/Wessel/Dropbox/Resources',
    'catalogue_path': '/Users/Wessel/Dropbox/Projects/Development/Catalogue',
    'base_path': '/Users/Wessel/Dropbox',
    'binaries': {'find': '/usr/bin/find',
                 'mdfind': '/usr/bin/mdfind',
                 'fzf': '/usr/local/bin/fzf',
                 'subl': '/usr/local/bin/subl',
                 'pbpaste': '/usr/bin/pbpaste',
                 'trash': '/usr/local/bin/trash'},
    'feedback_sleep': 2
}

# Bib config
names = [
    'Gaussian',
    'IEEE',
    'Copula'
]

replacements = [
    ('&', '\\&'),
    ('Alvarez', "{\\'A}lvarez")
]
