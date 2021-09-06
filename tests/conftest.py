import pytest

from sixi_web import API


@pytest.fixture
def api():
    return API(templates_dir="tests/templates")


@pytest.fixture
def client(api):
    return api.test_client()
