import errno
import flask
import glob
import os
import shutil

from .base import AnnexBase

__all__ = ('FileAnnex',)

# -----------------------------------------------------------------------------


class FileAnnex(AnnexBase):
    def __init__(self, root_path):
        self._root_path = root_path

    def _get_filename(self, key):
        return flask.safe_join(self._root_path, key)

    def delete(self, key):
        os.unlink(self._get_filename(key))

        # Clean up empty directories.
        key_dir_name = os.path.dirname(key)
        while key_dir_name:
            dir_name = self._get_filename(key_dir_name)
            if os.listdir(dir_name):
                break

            os.rmdir(dir_name)
            key_dir_name = os.path.dirname(key_dir_name)

    def delete_many(self, keys):
        for key in keys:
            self.delete(key)

    def get_file(self, key, out_filename):
        in_filename = self._get_filename(key)
        shutil.copyfile(in_filename, out_filename)

    def list_keys(self, prefix):
        pattern = self._get_filename('{}*'.format(prefix))
        filenames = glob.glob(pattern)

        return [
            os.path.relpath(filename, self._root_path)
            for filename in filenames
        ]

    def save_file(self, key, in_filename):
        out_filename = self._get_filename(key)

        # Create directory for file if needed.
        key_dir_name = os.path.dirname(key)
        if key_dir_name:
            dir_name = self._get_filename(key_dir_name)
            try:
                os.makedirs(dir_name)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        shutil.copyfile(in_filename, out_filename)

    def send_file(self, key, **options):
        return flask.send_from_directory(self._root_path, key, **options)
