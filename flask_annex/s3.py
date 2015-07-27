from boto.s3.connection import S3Connection
from boto.s3.key import Key
import flask

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

    def save_file(self, key, filename):
        s3_key = Key(self._bucket, key)
        s3_key.set_contents_from_filename(filename)

    def send_file(self, key, **options):
        s3_key = Key(self._bucket, key)
        return flask.redirect(s3_key.generate_url(self._url_expires_in))
