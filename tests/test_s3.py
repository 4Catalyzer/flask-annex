from io import BytesIO

import pytest

from flask_annex import Annex

from helpers import AbstractTestAnnex, assert_key_value

# -----------------------------------------------------------------------------

try:
    import boto3
    from moto import mock_s3
except ImportError:
    pytestmark = pytest.mark.skipif(True, reason="S3 support not installed")

# -----------------------------------------------------------------------------


@pytest.yield_fixture
def bucket_name():
    with mock_s3():
        bucket = boto3.resource('s3').Bucket('flask-annex')
        bucket.create()

        yield bucket.name


# -----------------------------------------------------------------------------


class TestS3Annex(AbstractTestAnnex):
    @pytest.fixture
    def annex_base(self, bucket_name):
        return Annex('s3', bucket_name=bucket_name)

    def test_save_file_unknown_type(self, annex):
        annex.save_file('foo/qux', BytesIO(b'6\n'))
        assert_key_value(annex, 'foo/qux', b'6\n')

    def test_send_file(self, app, annex):
        with app.test_request_context():
            response = annex.send_file('foo/baz.json')

        assert response.status_code == 302


class TestS3AnnexFromEnv(TestS3Annex):
    @pytest.fixture
    def annex_base(self, monkeypatch, bucket_name):
        monkeypatch.setenv('FLASK_ANNEX_STORAGE', 's3')
        monkeypatch.setenv('FLASK_ANNEX_S3_BUCKET_NAME', bucket_name)
        monkeypatch.setenv('FLASK_ANNEX_S3_REGION', 'us-east-1')

        return Annex.from_env('FLASK_ANNEX')
