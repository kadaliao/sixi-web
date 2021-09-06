import pytest

from sixi_web import API, __version__

CSS_FILE_DIR = "css"
CSS_FILE_NAME = "main.css"
CSS_FILE_CONTENTS = "body {back_ground-color: red}"

TEMPLATE_FILE_NAME = "index.html"
TEMPLATE_FILE_CONTENTS = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width" />
    <title>{{ title }}</title>
  </head>
  <body>
    <h1>{{ name }}</h1>
  </body>
</html>
"""


def _create_static(static_dir):
    asset = static_dir.mkdir(CSS_FILE_DIR).join(CSS_FILE_NAME)
    asset.write(CSS_FILE_CONTENTS)
    return asset


def _create_templates(static_dir):
    asset = static_dir.join(TEMPLATE_FILE_NAME)
    asset.write(TEMPLATE_FILE_CONTENTS)
    return asset


def test_version():
    assert __version__ == "0.1.0"


def test_route_adding(api):
    @api.route("/home")
    def home(req, resp):
        resp.text = "for testing"


def test_conflict_route_adding(api):
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


def test_route_adding_use_method(api, client):
    RESP_TEXT = "route added"

    def home(req, resp):
        resp.text = RESP_TEXT

    api.add_route("/", home)

    assert client.get("/").text == RESP_TEXT


def test_template(tmpdir_factory):
    templates_dir = tmpdir_factory.mktemp("templates")
    _create_templates(templates_dir)
    api = API(templates_dir=str(templates_dir))
    client = api.test_client()

    @api.route("/html")
    def html_view(req, resp):
        resp.body = api.template(TEMPLATE_FILE_NAME, context=dict(title="Test Title", name="Test Name")).encode()

    resp = client.get("/html")

    assert "text/html" in resp.headers["Content-Type"]
    assert "Test Title" in resp.text
    assert "Test Name" in resp.text


def test_custom_error_handler(api, client):
    def error_handler(req, resp, error):
        resp.text = f"Exception occured: {str(error)}"

    api.add_error_handler(AttributeError, error_handler)

    @api.route("/error")
    def error(req, resp):
        resp.status_code = 400
        raise AttributeError("This should not be seen")

    resp = client.get("/error")
    assert "Exception occured" in resp.text


def test_custom_error_handler_decorator(api, client):
    @api.error_handler(AttributeError)
    def error_handler(req, resp, error):
        resp.text = f"Exception occured: {str(error)}"

    @api.route("/error")
    def error(req, resp):
        resp.status_code = 400
        raise AttributeError("This should not be seen")

    resp = client.get("/error")
    assert "Exception occured" in resp.text


def test_conflict_custom_error_handler(api):
    @api.error_handler(AttributeError)
    def error_handler(req, resp, error):
        resp.text = f"Exception occured: {str(error)}"

    with pytest.raises(AssertionError):

        @api.error_handler(AttributeError)
        def error_handler2(req, resp, error):
            resp.text = f"Exception occured: {str(error)}"


def test_404_if_no_static_file(client):
    assert client.get("/main.css").status_code == 404


def test_assets_are_served(tmpdir_factory):
    static_dir = tmpdir_factory.mktemp("static")
    _create_static(static_dir)
    api = API(static_dir=str(static_dir))
    client = api.test_client()

    resp = client.get(f"/{CSS_FILE_DIR}/{CSS_FILE_NAME}")

    assert resp.status_code == 200
    assert resp.text == CSS_FILE_CONTENTS
