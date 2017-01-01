from config import config
import subprocess as sp
import core.utils
import os


def find(path, follow_symlinks=True):
    """
    List files.
    :param path: path
    :param follow_symlinks: boolean whether to follow symlinks
    :return: list of files
    """
    args = [config['binaries']['find']]
    if follow_symlinks:
        args += ['-L']
    args += [path]
    out, _ = sp.Popen(args, stdout=sp.PIPE).communicate()
    return filter(None, out.split('\n'))


def mdfind(path, query):
    """
    Search for content.
    :param path: path
    :param query: query
    :return: list of files
    """
    args = [config['binaries']['mdfind'], '-onlyin', path, query]
    out, _ = sp.Popen(args, stdout=sp.PIPE).communicate()
    return filter(None, out.split('\n'))


def mdfind2(path, query):
    """
    Search for content, including symlinks.
    :param path: path
    :param query: query
    :return: list of files
    """
    files = core.utils.filter_ext(find(path), ['', '.pdf'])
    sym_paths = filter(os.path.islink, files)
    resolved_paths = map(os.path.realpath, sym_paths)
    # Search symbolic directories and return real directories
    dirs = filter(os.path.isdir, resolved_paths + [path])
    results = sum(map(lambda x: mdfind(x, query), set(dirs)), [])
    # Search symbolic files and return symbolic paths
    files = filter(lambda x: os.path.isfile(x[1]),
                   zip(sym_paths, resolved_paths))
    for sym_file, real_file in files:
        result = mdfind(os.path.dirname(real_file), query)
        if real_file in result:
            results.append(sym_file)
    return results


def fzf(input, query=None):
    """
    Search for name.
    :param input: text input
    :param query: query
    :return: list of files
    """
    args = [config['binaries']['fzf']]
    if query is not None:
        args += ['-f', query]
    p = sp.Popen(args, stdin=sp.PIPE, stdout=sp.PIPE)
    p.stdin.write(input)
    out, _ = p.communicate()
    return filter(None, out.split('\n'))


def pbpaste():
    """
    Paste from clipboard.
    :return: clipboard
    """
    out, _ = sp.Popen([config['binaries']['pbpaste']],
                      stdout=sp.PIPE).communicate()
    return out


def subl(path):
    """
    Open Sublime Text.
    :param path: path
    """
    sp.Popen([config['binaries']['subl'], path]).wait()


def list(extensions=None):
    """
    List files with certain extensions on `resource_path`.
    :param extensions: extensions
    :return: list of files
    """
    files = find(config['resource_path'])
    if extensions is None:
        return files
    else:
        return core.utils.filter_ext(files, extensions)


def trash(path):
    """
    Move a file to trash.
    :param path: path
    """
    sp.Popen([config['binaries']['trash'], path]).wait()
