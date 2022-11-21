import pytest
from app import app as APP

@pytest.fixture()
def app():
    APP.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield APP

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()
