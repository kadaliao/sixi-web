import pytest

from sixi_web import __version__


def test_version():
    assert __version__ == "0.1.0"


def test_route_adding(api):
    @api.route("/home")
    def home(req, resp):
        resp.text = "for testing"


def test_config_route_adding(api):
    @api.route("/home")
    def home(req, resp):
        resp.text = "for testing"

    with pytest.raises(AssertionError):

        @api.route("/home")
        def home2(req, resp):
            resp.text = "for testing too"


def test_client_sending_requests(api, client):
    RESP_TEXT = "All is good."

    @api.route("/hi")
    def hi(req, resp):
        resp.text = RESP_TEXT

    assert client.get("/hi").text == RESP_TEXT


def test_parametrized_route(api, client):
    @api.route("/{name}")
    def greeting(req, resp, name):
        resp.text = f"Hi {name}"

    assert client.get("/matthew").text == "Hi matthew"
    assert client.get("/ashley").text == "Hi ashley"


def test_default_404_response(client):
    resp = client.get("/404")
    assert "not found" in resp.text.lower()
    assert resp.status_code == 404


def test_class_based_view_post(api, client):
    resp_text = "testing for post"

    @api.route("/todo")
    class TodoResource:
        def post(self, req, resp):
            resp.text = resp_text

    assert client.post("/todo").text == resp_text


def test_class_based_view_get(api, client):
    resp_text = "testing for get"

    @api.route("/todo")
    class TodoResource:
        def get(self, req, resp):
            resp.text = resp_text

    assert client.get("/todo").text == resp_text


def test_class_based_view_method_not_allowed(api, client):
    @api.route("/todo")
    class TodoResource:
        def post(self, req, resp):
            resp.text = "hello"

    with pytest.raises(AttributeError):
        client.get("/todo")
