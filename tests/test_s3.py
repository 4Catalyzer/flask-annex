import base64
from io import BytesIO
import json

import pytest

from flask_annex import Annex

from helpers import AbstractTestAnnex, assert_key_value, get_upload_info

# -----------------------------------------------------------------------------

try:
    import boto3
    from moto import mock_s3
    import requests
except ImportError:
    pytestmark = pytest.mark.skipif(True, reason="S3 support not installed")

# -----------------------------------------------------------------------------


@pytest.yield_fixture
def bucket_name():
    with mock_s3():
        bucket = boto3.resource('s3').Bucket('flask-annex')
        bucket.create()

        yield bucket.name


def get_policy(upload_info):
    return json.loads(
        base64.urlsafe_b64decode(
            upload_info['data']['policy'].encode(),
        ).decode(),
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
        return Annex('s3', bucket_name)

    def test_save_file_unknown_type(self, annex):
        annex.save_file('foo/qux', BytesIO(b'6\n'))
        assert_key_value(annex, 'foo/qux', b'6\n')

    def test_send_file(self, client):
        response = client.get('/file/foo/baz.json')
        assert response.status_code == 302

        s3_url = response.headers['Location']

        # FIXME: Moto doesn't support response-content-disposition, so assert
        # on the generated URL rather than Moto's response.
        assert 'response-content-disposition=attachment' in s3_url

        s3_response = requests.get(s3_url)
        assert s3_response.status_code == 200

        # FIXME: Workaround for spulec/moto#657.
        assert 'application/json' in s3_response.headers['Content-Type']

    def test_get_upload_info(self, client):
        upload_info = get_upload_info(client, 'foo/qux.txt')

        assert upload_info['method'] == 'POST'
        assert upload_info['url'] == 'https://flask-annex.s3.amazonaws.com/'
        assert upload_info['data']['key'] == 'foo/qux.txt'
        assert upload_info['data']['Content-Type'] == 'text/plain'

        conditions = get_policy(upload_info)['conditions']
        assert get_condition(conditions, 'bucket') == 'flask-annex'
        assert get_condition(conditions, 'key') == 'foo/qux.txt'
        assert get_condition(conditions, 'Content-Type') == 'text/plain'

    def test_get_upload_info_max_content_length(self, app, client):
        app.config['MAX_CONTENT_LENGTH'] = 100

        upload_info = get_upload_info(client, 'foo/qux.txt')

        conditions = get_policy(upload_info)['conditions']
        assert get_condition(conditions, 'content-length-range') == [0, 100]


class TestS3AnnexFromEnv(TestS3Annex):
    @pytest.fixture
    def annex_base(self, monkeypatch, bucket_name):
        monkeypatch.setenv('FLASK_ANNEX_STORAGE', 's3')
        monkeypatch.setenv('FLASK_ANNEX_S3_BUCKET_NAME', bucket_name)
        monkeypatch.setenv('FLASK_ANNEX_S3_REGION', 'us-east-1')

        return Annex.from_env('FLASK_ANNEX')
