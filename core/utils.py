import os


def ext_change(path, new_extension):
    """ Change the extension of a file. """
    base, current_extension = os.path.splitext(path)
    if new_extension:
        return base + new_extension
    return base


def filter_ext(files, extensions):
    """ Filter a list of files according to extensions. """
    return filter(lambda x: os.path.splitext(x)[1] in extensions, files)
