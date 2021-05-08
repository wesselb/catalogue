import os

import catalogue.bin
from config import config


def ext_change(path, new_extension):
    """Change the extension of a file.

    Args:
        path (str): Current path.
        new_extension (str): New extension.

    Returns:
        str: New path.

    """
    base, current_extension = os.path.splitext(path)
    if not new_extension.startswith("."):
        new_extension = "." + new_extension
    return base + new_extension


def file_filter(files, extensions):
    """Filter a list of files according to extensions.

    Args:
        files (list[str]): List of files.
        extensions (str, list[str], or None): Extension or extensions to filter
            for. `None` represents a directory.

    Returns:
        list[str]: Filtered list of files.
    """
    extensions = extensions if isinstance(extensions, list) else [extensions]

    def okay(x):
        _, ext = os.path.splitext(x)
        return ext in extensions or (None in extensions and os.path.isdir(x))

    return filter(okay, files)


def list_files(extensions=None):
    """List files with certain extensions on `resource_path`.

    Args:
        extensions (str, list[str], or None, optional): Extensions to list.

    Returns:
        list[str]: List of files.
    """
    files = catalogue.bin.find(config["resource_path"])
    if extensions is None:
        return files
    else:
        return file_filter(files, extensions)
