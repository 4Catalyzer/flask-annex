import pytest

from flask_annex import Annex

# -----------------------------------------------------------------------------


def test_unknown_annex():
    with pytest.raises(ValueError):
        Annex("unknown")


def test_unknown_annex_from_env(monkeypatch):
    monkeypatch.setenv("FLASK_ANNEX_STORAGE", "unknown")

    with pytest.raises(ValueError):
        Annex.from_env("FLASK_ANNEX")
