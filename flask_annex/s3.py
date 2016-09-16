import mimetypes

import boto3
import flask

from .base import AnnexBase
from .compat import string_types

# -----------------------------------------------------------------------------

DEFAULT_URL_EXPIRES_IN = 300

# -----------------------------------------------------------------------------


class S3Annex(AnnexBase):
    def __init__(
        self,
        bucket_name,
        region=None,
        access_key_id=None,
        secret_access_key=None,
        url_expires_in=DEFAULT_URL_EXPIRES_IN,
    ):
        self._client = boto3.client(
            's3',
            region,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )

        self._bucket_name = bucket_name
        self._url_expires_in = url_expires_in

    def delete(self, key):
        self._client.delete_object(Bucket=self._bucket_name, Key=key)

    def delete_many(self, keys):
        self._client.delete_objects(
            Bucket=self._bucket_name,
            Delete={
                'Objects': tuple({'Key': key} for key in keys),
            },
        )

    def get_file(self, key, out_file):
        if isinstance(out_file, string_types):
            self._client.download_file(self._bucket_name, key, out_file)
        else:
            self._client.download_fileobj(self._bucket_name, key, out_file)

    def list_keys(self, prefix):
        response = self._client.list_objects_v2(
            Bucket=self._bucket_name, Prefix=prefix,
        )
        if 'Contents' not in response:
            return ()
        return tuple(item['Key'] for item in response['Contents'])

    def save_file(self, key, in_file):
        # Get the content type from the key, rather than letting Boto try to
        # figure it out from the file's name, which may be uninformative.
        content_type = mimetypes.guess_type(key)[0]
        if content_type:
            extra_args = {'ContentType': content_type}
        else:
            extra_args = None

        if isinstance(in_file, string_types):
            self._client.upload_file(
                in_file, self._bucket_name, key, extra_args,
            )
        else:
            self._client.upload_fileobj(
                in_file, self._bucket_name, key, extra_args,
            )

    def send_file(self, key):
        url = self._client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self._bucket_name,
                'Key': key,
            },
        )
        return flask.redirect(url)
