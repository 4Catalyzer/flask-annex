import boto3
import flask
import mimetypes

from .base import AnnexBase

# -----------------------------------------------------------------------------

DEFAULT_EXPIRES_IN = 300

MISSING = object()

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
    ):
        self._client = boto3.client(
            "s3",
            region,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
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
        response = self._client.list_objects_v2(
            Bucket=self._bucket_name,
            Prefix=prefix,
        )
        if "Contents" not in response:
            return ()
        return tuple(item["Key"] for item in response["Contents"])

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

    def send_file(self, key):
        url = self._client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": self._bucket_name,
                "Key": key,
                # We don't need to specify filename explicitly; the basename
                # of the key is in the URL and is appropriate here.
                "ResponseContentDisposition": "attachment",
            },
            ExpiresIn=self._expires_in,
        )
        return flask.redirect(url)

    def get_upload_info(self, key):
        fields = {}
        conditions = []

        content_type = mimetypes.guess_type(key)[0]
        if content_type:
            fields["Content-Type"] = content_type

        if self._max_content_length is not MISSING:
            max_content_length = self._max_content_length
        else:
            max_content_length = flask.current_app.config["MAX_CONTENT_LENGTH"]
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

        return {
            "method": "POST",
            "url": post_info["url"],
            "post_data": tuple(post_info["fields"].items()),
        }
