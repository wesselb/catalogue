import sys
import core.alfred
import subprocess as sp


if len(sys.argv) < 2:
    exit('Insufficient arguments')

query_type = sys.argv[1]
query = ' '.join(sys.argv[2:])

if query_type not in ['name', 'content']:
    exit('Type must be either \'name\' or \'content\'')

script_path = '/Users/Wessel/Dropbox/Projects/Development/' \
              'Catalogue/find_{}.sh'.format(query_type)

p = sp.Popen([script_path, query], stdout=sp.PIPE)
out, _ = p.communicate()
files = filter(None, out.split('\n'))
print core.alfred.AlfredFormatter(files, '/Users/Wessel/Dropbox/').list_json()
