from flask import Flask
import pytest

# -----------------------------------------------------------------------------


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True

    return app
