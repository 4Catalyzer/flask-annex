from io import BytesIO
import json

import pytest

# -----------------------------------------------------------------------------


def assert_key_value(annex, key, value):
    out_file = BytesIO()
    annex.get_file(key, out_file)

    out_file.seek(0)
    assert out_file.read() == value


def get_upload_info(client, key):
    response = client.get('/upload_info/{}'.format(key))
    return json.loads(response.get_data(as_text=True))


# -----------------------------------------------------------------------------


class AbstractTestAnnex(object):
    @pytest.fixture
    def annex(self, annex_base):
        annex_base.save_file('foo/bar.txt', BytesIO(b'1\n'))
        annex_base.save_file('foo/baz.json', BytesIO(b'2\n'))
        return annex_base

    @pytest.fixture(autouse=True)
    def routes(self, app, annex):
        @app.route('/file/<path:key>')
        def file(key):
            return annex.send_file(key)

        @app.route('/upload_info/<path:key>')
        def upload_info(key):
            return annex.get_upload_info(key)

    def test_get_file(self, annex):
        assert_key_value(annex, 'foo/bar.txt', b'1\n')

    def test_get_filename(self, tmpdir, annex):
        out_filename = tmpdir.join('out').strpath
        annex.get_file('foo/bar.txt', out_filename)
        assert open(out_filename).read() == '1\n'

    def test_list_keys(self, annex):
        assert sorted(annex.list_keys('foo/')) == [
            'foo/bar.txt',
            'foo/baz.json',
        ]

    def test_save_file(self, annex):
        annex.save_file('qux/foo.txt', BytesIO(b'3\n'))
        assert_key_value(annex, 'qux/foo.txt', b'3\n')

    def test_save_filename(self, tmpdir, annex):
        in_file = tmpdir.join('in')
        in_file.write('4\n')

        annex.save_file('qux/bar.txt', in_file.strpath)
        assert_key_value(annex, 'qux/bar.txt', b'4\n')

    def test_replace_file(self, annex):
        assert_key_value(annex, 'foo/bar.txt', b'1\n')
        annex.save_file('foo/bar.txt', BytesIO(b'5\n'))
        assert_key_value(annex, 'foo/bar.txt', b'5\n')

    def test_delete(self, annex):
        assert annex.list_keys('foo/bar.txt')
        annex.delete('foo/bar.txt')
        assert not annex.list_keys('foo/bar.txt')

    def test_delete_many(self, annex):
        assert annex.list_keys('')
        annex.delete_many(('foo/bar.txt', 'foo/baz.json'))
        assert not annex.list_keys('')
