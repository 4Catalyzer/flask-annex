import errno
import os
import shutil

import flask

from .base import AnnexBase
from .compat import recursive_glob, string_types

# -----------------------------------------------------------------------------


class FileAnnex(AnnexBase):
    def __init__(self, root_path):
        self._root_path = root_path

    def _get_filename(self, key):
        return flask.safe_join(self._root_path, key)

    def delete(self, key):
        try:
            os.unlink(self._get_filename(key))
        except OSError as e:
            if e.errno != errno.ENOENT:
                # It's fine if the file doesn't exist.
                raise  # pragma: no cover

        self._clean_empty_dirs(key)

    def _clean_empty_dirs(self, key):
        key_dir_name = os.path.dirname(key)

        while key_dir_name:
            dir_name = self._get_filename(key_dir_name)
            try:
                os.rmdir(dir_name)
            except OSError as e:
                if e.errno == errno.ENOTEMPTY:
                    break
                if e.errno != errno.ENOENT:
                    raise  # pragma: no cover

            key_dir_name = os.path.dirname(key_dir_name)

    def delete_many(self, keys):
        for key in keys:
            self.delete(key)

    def get_file(self, key, out_file):
        in_filename = self._get_filename(key)

        if isinstance(out_file, string_types):
            shutil.copyfile(in_filename, out_file)
        else:
            with open(in_filename, 'rb') as in_fp:
                shutil.copyfileobj(in_fp, out_file)

    def list_keys(self, prefix):
        root = self._get_filename(prefix)
        filenames = (root,) if os.path.isfile(root) else recursive_glob(root)

        return tuple(
            os.path.relpath(filename, self._root_path)
            for filename in filenames,
        )

    def save_file(self, key, in_file):
        out_filename = self._get_filename(key)
        self._ensure_key_dir(key)

        if isinstance(in_file, string_types):
            shutil.copyfile(in_file, out_filename)
        else:
            with open(out_filename, 'wb') as out_fp:
                shutil.copyfileobj(in_file, out_fp)

    def _ensure_key_dir(self, key):
        dir_name = self._get_filename(os.path.dirname(key))
        if os.path.exists(dir_name):
            return

        # Verify that we aren't trying to create the root path.
        if not os.path.exists(self._root_path):
            raise IOError(
                "root path {} does not exist".format(self._root_path),
            )

        try:
            os.makedirs(dir_name)
        except OSError as e:  # pragma: no cover
            if e.errno != errno.EEXIST:
                raise

    def send_file(self, key):
        return flask.send_from_directory(
            self._root_path, key,
            as_attachment=True,
            attachment_filename=os.path.basename(key),
        )

    def get_upload_info(self, key):
        raise NotImplementedError("file annex does not support upload info")
