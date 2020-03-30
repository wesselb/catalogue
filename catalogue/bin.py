import os
import subprocess as sp

from config import config
from .utils import file_filter


def find(path, follow_symlinks=True):
    """List files.

    Args:
        path (str): Path.
        follow_symlinks (bool): Follow symlink.

    Returns:
        list[str]: List of files.
    """
    args = [config['binaries']['find']]
    if follow_symlinks:
        args += ['-L']
    args += [path]
    out, _ = sp.Popen(args, stdout=sp.PIPE).communicate()
    return filter(None, out.decode().split("\n"))


def mdfind(path, query):
    """Search for content.

    Args:
        path (str): Path to search on.
        query (str): Query to search for.

    Returns:
        list[str]: List of files that match the search query.
    """
    # Search in path.
    args = [config['binaries']['mdfind'], '-onlyin', path, query]
    out, _ = sp.Popen(args, stdout=sp.PIPE).communicate()
    results = filter(None, out.decode().split('\n'))

    # Search for symlinked folders.
    files = file_filter(find(path, follow_symlinks=True), None)
    sym_paths = map(os.path.realpath, filter(os.path.islink, files))

    # Recurse and return.
    return results + [r for p in sym_paths for r in mdfind(p, query)]


def fzf(input, query=None):
    """Fuzzy search.

    Args:
        input (str): Input to search through.
        query (str): Query.

    Returns:
        list[str]: Fuzzy matches.
    """
    args = [config['binaries']['fzf']]
    if query is not None:
        args += ['-f', query]
    p = sp.Popen(args, stdin=sp.PIPE, stdout=sp.PIPE)
    p.stdin.write(input.encode())
    out, _ = p.communicate()
    return filter(None, out.decode().split('\n'))


def pbcopy(x):
    """Copy text to clipboard.

    Args:
        x (str): Text to copy.
    """
    sp.Popen([config['binaries']['pbcopy']],
             stdout=sp.PIPE, stdin=sp.PIPE).communicate(input=x.encode())


def pbpaste():
    """Paste text from clipboard.

    Returns:
        str:Text from clipboard.
    """
    out, _ = sp.Popen([config['binaries']['pbpaste']],
                      stdout=sp.PIPE).communicate()
    return out.decode()


def subl(path):
    """Open Sublime Text.

    Args:
        path (str): File to open.
    """
    sp.Popen([config['binaries']['subl'], path]).wait()


def trash(path):
    """Move a file to trash.

    Args:
        path (str): Path.
    """
    sp.Popen([config['binaries']['trash'], path]).wait()
