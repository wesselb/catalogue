import os


def ext_change(path, new_extension):
    """
    Change the extension of a file.
    :param path: path
    :param new_extension: new extension
    :return: path with new extension
    """
    base, current_extension = os.path.splitext(path)
    if new_extension:
        return base + new_extension
    return base


def filter_ext(files, extensions):
    """
    Filter a list of files according to extensions where no extension refers to
    a directory.
    :param files: list of files
    :param extensions: list of extensions
    :return: filtered list of files
    """
    file_exts = filter(None, extensions)
    dir_allowed = '' in extensions
    return filter(lambda x: (os.path.splitext(x)[1] in file_exts
                             or (dir_allowed and os.path.isdir(x))), files)
