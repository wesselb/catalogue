import subprocess as sp
from config import config
import core.utils


def find(path, follow_symlinks=True):
    args = [config['binaries']['find']]
    if follow_symlinks:
        args += ['-L']
    args += [path]
    out, _ = sp.Popen(args, stdout=sp.PIPE).communicate()
    return filter(None, out.split('\n'))


def mdfind(path, query):
    args = [config['binaries']['mdfind'], '-onlyin', path, query]
    out, _ = sp.Popen(args, stdout=sp.PIPE).communicate()
    return filter(None, out.split('\n'))


def fzf(input, query=None):
    args = [config['binaries']['fzf']]
    if query is not None:
        args += ['-f', query]
    p = sp.Popen(args, stdin=sp.PIPE, stdout=sp.PIPE)
    p.stdin.write(input)
    out, _ = p.communicate()
    return filter(None, out.split('\n'))


def pbpaste():
    out, _ = sp.Popen([config['binaries']['pbpaste']],
                      stdout=sp.PIPE).communicate()
    return out


def subl(path):
    sp.Popen([config['binaries']['subl'], path]).wait()


def list(extensions):
    files = find(config['resource_path'])
    return core.utils.filter_ext(files, extensions)


def trash(path):
    sp.Popen([config['binaries']['trash'], path]).wait()
