import flask
import json
import pytest
from io import BytesIO

# -----------------------------------------------------------------------------


def assert_key_value(annex, key, value):
    out_file = BytesIO()
    annex.get_file(key, out_file)

    out_file.seek(0)
    assert out_file.read() == value


def get_upload_info(client, key, **kwargs):
    response = client.get(f"/upload_info/{key}", **kwargs)
    return json.loads(response.get_data(as_text=True))


# -----------------------------------------------------------------------------


class AbstractTestAnnex:
    @pytest.fixture
    def annex(self, annex_base):
        annex_base.save_file("foo/bar.txt", BytesIO(b"1\n"))
        annex_base.save_file("foo/baz.json", BytesIO(b"2\n"))
        return annex_base

    @pytest.fixture(autouse=True)
    def routes(self, app, annex):
        @app.route("/files/<path:key>", methods=("GET", "PUT"))
        def file(key):
            if flask.request.method != "GET":
                raise NotImplementedError()
            return annex.send_file(key)

        @app.route("/upload_info/<path:key>")
        def upload_info(key):
            try:
                known_query_args = {
                    "max_content_length": flask.request.args.get(
                        "max_content_length", type=int
                    )
                }
                upload_info = annex.get_upload_info(
                    key,
                    **{
                        k: v
                        for k, v in known_query_args.items()
                        if k in flask.request.args
                    },
                )
            except NotImplementedError:
                upload_info = {
                    "method": "PUT",
                    "url": flask.url_for(
                        "file",
                        key=key,
                        _method="PUT",
                        _external=True,
                    ),
                    "headers": {
                        "Authorization": flask.request.headers.get(
                            "Authorization",
                        ),
                    },
                }

            return flask.jsonify(upload_info)

    def test_get_file(self, annex):
        assert_key_value(annex, "foo/bar.txt", b"1\n")

    def test_get_filename(self, tmpdir, annex):
        out_filename = tmpdir.join("out").strpath
        annex.get_file("foo/bar.txt", out_filename)
        assert open(out_filename).read() == "1\n"

    def test_list_keys(self, annex):
        annex.save_file("foo/qux.txt", BytesIO(b"3\n"))
        assert sorted(annex.list_keys("foo/")) == [
            "foo/bar.txt",
            "foo/baz.json",
            "foo/qux.txt",
        ]

        # check that dangling '/' is not relevant
        assert sorted(annex.list_keys("foo/")) == sorted(
            annex.list_keys("foo")
        )

    def test_list_keys_nested(self, annex):
        assert sorted(annex.list_keys("foo/")) == [
            "foo/bar.txt",
            "foo/baz.json",
        ]

    def test_save_file(self, annex):
        annex.save_file("qux/foo.txt", BytesIO(b"3\n"))
        assert_key_value(annex, "qux/foo.txt", b"3\n")

    def test_save_filename(self, tmpdir, annex):
        in_file = tmpdir.join("in")
        in_file.write("4\n")

        annex.save_file("qux/bar.txt", in_file.strpath)
        assert_key_value(annex, "qux/bar.txt", b"4\n")

    def test_replace_file(self, annex):
        assert_key_value(annex, "foo/bar.txt", b"1\n")
        annex.save_file("foo/bar.txt", BytesIO(b"5\n"))
        assert_key_value(annex, "foo/bar.txt", b"5\n")

    def test_delete(self, annex):
        assert tuple(annex.list_keys("foo/bar.txt"))
        annex.delete("foo/bar.txt")
        assert not tuple(annex.list_keys("foo/bar.txt"))

    def test_delete_nonexistent(self, annex):
        annex.delete("@@nonexistent")

    def test_delete_many(self, annex):
        assert tuple(annex.list_keys(""))
        annex.delete_many(("foo/bar.txt", "foo/baz.json", "foo/@@nonexistent"))
        assert not tuple(annex.list_keys(""))
