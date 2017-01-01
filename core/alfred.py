import os
import json


class AlfredFormatter:
    """
    Format a list of files according to Alfred's format.
    :param files: list of files
    :param base_path: show paths of files relative to `base_path`
    """

    def __init__(self, files, base_path):
        self._files = files
        self._base_path = base_path

    def list_json(self):
        """
        List the files in Alfred's JSON format.
        :return: JSON
        """
        json_out = {'items': map(self._file_to_json, self._files)}
        return json.dumps(json_out, indent=4)

    def _trim_path(self, file_path):
        """ Trim a path by removing its prefix. """
        if file_path.startswith(self._base_path):
            return file_path[len(self._base_path):]
        else:
            return file_path

    def _file_to_json(self, file_path):
        """ Convert a file to JSON. """
        _, extension = os.path.splitext(file_path)
        # If 'uid' is specified, then and only then will Alfred order the
        # entries
        return {  # 'uid': file_path,
                'type': 'file',
                'title': os.path.basename(file_path),
                'subtitle': self._trim_path(file_path),
                'quicklookurl': file_path,
                'arg': file_path,
                'icon': {'type': 'fileicon',
                         'path': file_path}}
