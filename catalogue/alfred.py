# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import os
import json

__all__ = ['list_json']


def list_json(files, base_path):
    """
    List the files in Alfred's JSON format.

    Args:
        files: Files to list.
        base_path: Base path of the files.

    Returns:
        JSON.
    """
    json_out = {'items': [_file_to_json_converter(base_path)(file)
                          for file in files]}
    return json.dumps(json_out, indent=4)


def _trim_path(file_path, base_path):
    """
    Trim a path by removing a prefix.

    Args:
        file_path: Path.
        base_path: Prefix to remove.

    Returns:
        Trimmed path.
    """
    if file_path.startswith(base_path):
        return file_path[len(base_path):]
    return file_path


def _file_to_json_converter(base_path):
    """
    Generate a function that converters file paths to JSON, stripping a base
    path.

    Args:
        base_path: Base path.

    Returns:
        Function that converts file paths to JSON.
    """

    def converter(file_path):
        _, extension = os.path.splitext(file_path)
        # If 'uid' is specified, then and only then will Alfred order the
        # entries
        return {'type': 'file',
                'title': os.path.basename(file_path),
                'subtitle': _trim_path(file_path, base_path),
                'quicklookurl': file_path,
                'arg': file_path,
                'icon': {'type': 'fileicon',
                         'path': file_path}}

    return converter
