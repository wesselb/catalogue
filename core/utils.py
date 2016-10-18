import os


def ext_change(path, new_extension):
    base, current_extension = os.path.splitext(path)
    if new_extension:
        return base + new_extension
    return base
