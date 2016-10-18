import os
import json


class AlfredFormatter:
    """
    Format a list of files according to Alfred's format.

    :param files: List of files
    :param base_path: Show paths of files relative to ``base_path``
    """

    def __init__(self, files, base_path):
        self._files = files
        self._base_path = base_path

    def list_json(self):
        json_out = {'items': map(self._file_to_json, self._files)}
        return json.dumps(json_out, indent=4)

    def _trim_path(self, file_path):
        if file_path.startswith(self._base_path):
            return file_path[len(self._base_path):]
        else:
            return file_path

    def _file_to_json(self, file_path):
        _, extension = os.path.splitext(file_path)
        return {'uid': file_path,
                'type': 'file',
                'title': os.path.basename(file_path),
                'subtitle': self._trim_path(file_path),
                # 'quicklookurl': '',
                'arg': file_path,
                'icon': {'type': 'fileicon',
                         'path': file_path}}
