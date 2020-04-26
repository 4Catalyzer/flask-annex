import pytest
from flask import Flask

# -----------------------------------------------------------------------------


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True

    return app


@pytest.fixture
def client(app):
    return app.test_client()
