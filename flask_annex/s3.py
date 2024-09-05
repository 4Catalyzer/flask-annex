import boto3
import flask
import mimetypes
from botocore.config import Config
from typing import Optional

from .base import AnnexBase

# -----------------------------------------------------------------------------

DEFAULT_EXPIRES_IN = 300

MISSING = object()


def is_defined(obj):
    return obj is not MISSING and obj is not None


# -----------------------------------------------------------------------------


class S3Annex(AnnexBase):
    def __init__(
        self,
        bucket_name,
        *,
        region=None,
        access_key_id=None,
        secret_access_key=None,
        expires_in=DEFAULT_EXPIRES_IN,
        max_content_length=MISSING,
        config: Optional[Config] = None,
    ):
        self._client = boto3.client(
            "s3",
            region,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            config=config,
        )

        self._bucket_name = bucket_name
        self._expires_in = expires_in
        self._max_content_length = max_content_length

    def delete(self, key):
        self._client.delete_object(Bucket=self._bucket_name, Key=key)

    def delete_many(self, keys):
        # casting to tuple because keys might be iterable
        objects = tuple({"Key": key} for key in keys)
        if not objects:
            # boto fails if the array is empty.
            return

        self._client.delete_objects(
            Bucket=self._bucket_name,
            Delete={"Objects": objects},
        )

    def get_file(self, key, out_file):
        if isinstance(out_file, str):
            self._client.download_file(self._bucket_name, key, out_file)
        else:
            self._client.download_fileobj(self._bucket_name, key, out_file)

    def list_keys(self, prefix):
        paginator = self._client.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(
            Bucket=self._bucket_name, Prefix=prefix
        )

        return (
            item["Key"]
            for page in page_iterator
            if "Contents" in page
            for item in page["Contents"]
        )

    def save_file(self, key, in_file):
        # Get the content type from the key, rather than letting Boto try to
        # figure it out from the file's name, which may be uninformative. It's
        # better to do it here so S3 doesn't have a wrong content type, rather
        # than at read time as with content disposition.
        content_type = mimetypes.guess_type(key)[0]
        if content_type:
            extra_args = {"ContentType": content_type}
        else:
            extra_args = None

        if isinstance(in_file, str):
            self._client.upload_file(
                in_file,
                self._bucket_name,
                key,
                extra_args,
            )
        else:
            self._client.upload_fileobj(
                in_file,
                self._bucket_name,
                key,
                extra_args,
            )

    def generate_presigned_url(self, key, content_disposition=None):
        content_disposition = content_disposition or "attachment"
        return self._client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": self._bucket_name,
                "Key": key,
                "ResponseContentDisposition": content_disposition,
            },
            ExpiresIn=self._expires_in,
        )

    def send_file(self, key, content_disposition=None):
        url = self.generate_presigned_url(key, content_disposition)
        return flask.redirect(url)

    def get_upload_info(self, key, max_content_length=MISSING):
        fields = {}
        conditions = []

        content_type = mimetypes.guess_type(key)[0]
        if content_type:
            fields["Content-Type"] = content_type

        if is_defined(max_content_length):
            max_content_length = max_content_length
        elif is_defined(self._max_content_length):
            max_content_length = self._max_content_length
        elif flask.current_app.config["MAX_CONTENT_LENGTH"] is not None:
            max_content_length = flask.current_app.config["MAX_CONTENT_LENGTH"]
        else:
            max_content_length = None

        if max_content_length is not None:
            conditions.append(
                ("content-length-range", 0, max_content_length),
            )

        # Boto doesn't automatically add fields to conditions.
        for field_key, field_value in fields.items():
            conditions.append({field_key: field_value})

        post_info = self._client.generate_presigned_post(
            Bucket=self._bucket_name,
            Key=key,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=self._expires_in,
        )

        url = post_info["url"]

        # Coerce this to entries to ensure order remains as S3 expects.
        post_data = tuple(post_info["fields"].items())

        return {
            "method": "POST",
            "url": url,
            "post_data": post_data,
        }
