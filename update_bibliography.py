import subprocess as sp
import json
from core.bib import BibRenderer


p = sp.Popen(['/Users/Wessel/Dropbox/Projects/Development/'
              'Catalogue/list_json.sh'], stdout=sp.PIPE)
out, _ = p.communicate()
files = filter(None, out.split('\n'))

entries = []
for entry in files:
    with open(entry) as f:
        entries.extend(json.load(f))

with open('output/bibliography.bib', 'w') as f:
    f.write(BibRenderer(entries).as_text())

