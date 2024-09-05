import base64
import json
import pytest
from io import BytesIO
from unittest.mock import Mock

from flask_annex import Annex

from .helpers import AbstractTestAnnex, assert_key_value, get_upload_info

# -----------------------------------------------------------------------------

try:
    import boto3
    import requests
    from moto import mock_s3
except ImportError:
    pytestmark = pytest.mark.skipif(True, reason="S3 support not installed")

# -----------------------------------------------------------------------------


@pytest.fixture
def bucket_name():
    with mock_s3():
        bucket = boto3.resource("s3").Bucket("flask-annex")
        bucket.create()

        yield bucket.name


def get_policy(upload_info):
    # filter for the "policy" field; there should only be one instance
    policy_items = list(
        filter(lambda x: x[0] == "policy", upload_info["post_data"]),
    )
    policy_item = policy_items[0]

    return json.loads(
        base64.urlsafe_b64decode(policy_item[1].encode()).decode(),
    )


def get_condition(conditions, key):
    for condition in conditions:
        if isinstance(condition, list):
            if condition[0] == key:
                return condition[1:]
        else:
            if key in condition:
                return condition[key]

    raise KeyError()


# -----------------------------------------------------------------------------


class TestS3Annex(AbstractTestAnnex):
    @pytest.fixture
    def annex_base(self, bucket_name):
        return Annex("s3", bucket_name)

    def test_save_file_unknown_type(self, annex):
        annex.save_file("foo/qux", BytesIO(b"6\n"))
        assert_key_value(annex, "foo/qux", b"6\n")

    def test_send_file(self, client):
        response = client.get("/files/foo/baz.json")
        assert response.status_code == 302

        s3_url = response.headers["Location"]

        # FIXME: Moto doesn't support response-content-disposition, so assert
        # on the generated URL rather than Moto's response.
        assert "response-content-disposition=attachment" in s3_url

        s3_response = requests.get(s3_url)
        assert s3_response.status_code == 200

        # FIXME: Workaround for spulec/moto#657.
        assert "application/json" in s3_response.headers["Content-Type"]

    def test_get_upload_info(self, client):
        upload_info = get_upload_info(client, "foo/qux.txt")

        assert upload_info["method"] == "POST"
        assert upload_info["url"] == "https://flask-annex.s3.amazonaws.com/"
        assert upload_info["post_data"][0] == ["Content-Type", "text/plain"]
        assert upload_info["post_data"][1] == ["key", "foo/qux.txt"]
        assert upload_info["post_data"][2] == ["AWSAccessKeyId", "foobar_key"]
        assert upload_info["post_data"][3][0] == "policy"
        assert upload_info["post_data"][4][0] == "signature"

        conditions = get_policy(upload_info)["conditions"]
        assert get_condition(conditions, "bucket") == "flask-annex"
        assert get_condition(conditions, "key") == "foo/qux.txt"
        assert get_condition(conditions, "Content-Type") == "text/plain"

        self.assert_default_content_length_range(conditions)

    def assert_default_content_length_range(self, conditions):
        with pytest.raises(KeyError):
            get_condition(conditions, "content-length-range")

    def test_get_upload_info_max_content_length(self, app, client):
        app.config["MAX_CONTENT_LENGTH"] = 100

        upload_info = get_upload_info(client, "foo/qux.txt")

        conditions = get_policy(upload_info)["conditions"]
        self.assert_app_config_content_length_range(conditions)

    def assert_app_config_content_length_range(self, conditions):
        assert get_condition(conditions, "content-length-range") == [0, 100]

    def test_get_upload_info_unknown_content_type(self, client):
        upload_info = get_upload_info(client, "foo/qux.@@nonexistent")

        assert upload_info["method"] == "POST"
        assert upload_info["url"] == "https://flask-annex.s3.amazonaws.com/"

        # filter for the "key" field; there should be only one instance
        key_items = list(
            filter(lambda x: x[0] == "key", upload_info["post_data"]),
        )
        key_item = key_items[0]
        assert key_item[1] == "foo/qux.@@nonexistent"

        # should not have 'Content-Type' in the post data
        assert all(
            post_data_pair[0] != "Content-Type"
            for post_data_pair in upload_info["post_data"]
        )

    def test_delete_many_empty_list(self, annex, monkeypatch):
        mock = Mock()
        monkeypatch.setattr(annex._client, "delete_objects", mock)

        annex.delete_many(tuple())

        mock.assert_not_called()


class TestS3AnnexFromEnv(TestS3Annex):
    @pytest.fixture
    def annex_base(self, monkeypatch, bucket_name):
        monkeypatch.setenv("FLASK_ANNEX_STORAGE", "s3")
        monkeypatch.setenv("FLASK_ANNEX_S3_BUCKET_NAME", bucket_name)
        monkeypatch.setenv("FLASK_ANNEX_S3_REGION", "us-east-1")

        return Annex.from_env("FLASK_ANNEX")


class TestS3AnnexMaxContentLength(TestS3Annex):
    @pytest.fixture
    def annex_base(self, bucket_name):
        return Annex("s3", bucket_name, max_content_length=1000)

    def assert_default_content_length_range(self, conditions):
        assert get_condition(conditions, "content-length-range") == [0, 1000]

    def assert_app_config_content_length_range(self, conditions):
        assert get_condition(conditions, "content-length-range") == [0, 1000]
