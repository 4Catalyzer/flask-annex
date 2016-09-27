from io import BytesIO

import pytest

from flask_annex import Annex

from helpers import AbstractTestAnnex, assert_key_value

# -----------------------------------------------------------------------------


@pytest.fixture
def file_annex_path(tmpdir):
    return tmpdir.join('annex').mkdir().strpath


# -----------------------------------------------------------------------------


class TestFileAnnex(AbstractTestAnnex):
    @pytest.fixture
    def annex_base(self, file_annex_path):
        return Annex('file', file_annex_path)

    def test_save_file_existing_dir(self, annex):
        annex.save_file('foo/qux.txt', BytesIO(b'6\n'))
        assert_key_value(annex, 'foo/qux.txt', b'6\n')

    def test_send_file(self, client):
        response = client.get('/file/foo/baz.json')
        assert response.status_code == 200
        assert response.mimetype == 'application/json'

    def test_send_upload_info(self, annex):
        with pytest.raises(NotImplementedError):
            annex.send_upload_info('foo/qux.txt')


class TestFileAnnexFromEnv(TestFileAnnex):
    @pytest.fixture
    def annex_base(self, monkeypatch, file_annex_path):
        monkeypatch.setenv('FLASK_ANNEX_STORAGE', 'file')
        monkeypatch.setenv('FLASK_ANNEX_FILE_ROOT_PATH', file_annex_path)

        return Annex.from_env('FLASK_ANNEX')


# -----------------------------------------------------------------------------


def test_error_nonexistent_root_path(tmpdir):
    with pytest.raises(IOError):
        annex = Annex('file', tmpdir.join('dummy').strpath)
        annex.save_file('foo', BytesIO(b''))
