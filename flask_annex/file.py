import flask
import os
import shutil

from .base import AnnexBase

__all__ = ('FileAnnex',)

# -----------------------------------------------------------------------------


class FileAnnex(AnnexBase):
    def __init__(self, root_path):
        self._root_path = root_path

    def _get_filename(self, key, make_dirs=False):
        filename = os.path.join(self._root_path, key)

        if make_dirs:
            dir_name = os.path.dirname(filename)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

        return filename

    def save_file(self, key, in_filename):
        out_filename = self._get_filename(key, make_dirs=True)
        shutil.copyfile(in_filename, out_filename)

    def send_file(self, key, **options):
        return flask.send_from_directory(self._root_path, key, **options)
