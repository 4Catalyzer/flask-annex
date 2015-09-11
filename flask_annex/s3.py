from boto.s3.connection import S3Connection
from boto.s3.key import Key
import flask
from six import string_types
from werkzeug.datastructures import FileStorage

from .base import AnnexBase

__all__ = ('S3Annex',)

# -----------------------------------------------------------------------------

DEFAULT_URL_EXPIRES_IN = 300

# -----------------------------------------------------------------------------


class S3Annex(AnnexBase):
    def __init__(self, access_key_id, secret_access_key, bucket_name,
                 url_expires_in=DEFAULT_URL_EXPIRES_IN):
        self._connection = S3Connection(access_key_id, secret_access_key)
        self._bucket = self._connection.get_bucket(
            bucket_name, validate=False
        )

        self._url_expires_in = url_expires_in

    def _get_s3_key(self, key):
        return Key(self._bucket, key)

    def delete(self, key):
        s3_key = self._get_s3_key(key)
        s3_key.delete()

    def delete_many(self, keys):
        self._bucket.delete_keys(keys)

    def get_file(self, key, out_file):
        s3_key = self._get_s3_key(key)

        if isinstance(out_file, string_types):
            s3_key.get_contents_to_filename(out_file)
        else:
            s3_key.get_contents_to_file(out_file)

    def list_keys(self, prefix):
        return tuple(s3_key.name for s3_key in self._bucket.list(prefix))

    def save_file(self, key, in_file):
        s3_key = self._get_s3_key(key)

        if isinstance(in_file, string_types):
            s3_key.set_contents_from_filename(in_file)
        else:
            if isinstance(in_file, FileStorage):
                # Use filename for type inference instead of form name.
                s3_key.path = in_file.filename
                in_file = in_file.stream
            else:
                # Use key as fallback for guessing file type.
                s3_key.path = key
            s3_key.set_contents_from_file(in_file)

    def send_file(self, key):
        s3_key = self._get_s3_key(key)
        return flask.redirect(s3_key.generate_url(self._url_expires_in))
