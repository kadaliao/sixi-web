# sixi-web [![CI](https://github.com/kadaliao/sixi-web/actions/workflows/main-ci.yml/badge.svg?branch=main)](https://github.com/kadaliao/sixi-web/actions/workflows/main-ci.yml)

A simple web framework built for learning purpose.


## Installation

```sh
pip install sixi-web
```

## Development (uv)

This project is configured to use `uv` for dependency management and virtualenvs.

1) Create and sync the environment (includes dev tools):

```sh
uv venv
uv sync --dev
```

2) Run tests:

```sh
uv run pytest
```

3) Run the example app locally:

```sh
uv run gunicorn examples.app:app
```

4) Add dependencies:

```sh
# runtime dependency
uv add <package>

# dev-only dependency
uv add --dev <package>
```

<!-- USAGE EXAMPLES -->
## Usage

1. Import the Sixi web api instance to route. If you’ve used Flask before, you'll find it easy.

    ```python
    # app.py

    from sixi_web import API, Middleware

    app = API(templates_dir="templates", static_dir="static")


    @app.route("/")
    @app.route("/home")
    def index(req, resp):
        resp.text = "Hello world"


    @app.route("/about")
    def about(req, resp):
        resp.text = "A vegetable dog passing by."


    @app.route("/hello/{name}")
    def hello(req, resp, name):
        resp.text = f"Hello, {name}"


    @app.route("/add/{a:d}/{b:d}")
    def add(req, resp, a, b):
        result = int(a) + int(b)
        resp.text = f"{a} + {b} = {result}"


    @app.route("/todo")
    class TodoResource:
        def get(self, req, resp):
            resp.text = "Get a task"

        def post(self, req, resp):
            resp.text = "Create a task"


    @app.route("/html")
    def html(req, resp):
        resp.html = app.template("index.html", context=dict(title="hi", name="kada"))


    @app.route("/text")
    def text(req, resp):
        resp.text = "This is plain text"


    @app.route("/json")
    def json(req, resp):
        resp.json = dict(content="this is json")


    @app.error_handler(AttributeError)
    def attributeerror_handler(req, resp, e):
        resp.text = f"I got it, {e}"


    class PrintingMiddleware(Middleware):
        def process_request(self, req):
            print(f"request: {req}\n\n")

        def process_response(self, req, resp):
            print(f"response: {resp}\n\n")


    app.add_middleware(PrintingMiddleware)
    ```

2. Run with any WSGI application server such as Gunicorn.


    ```sh
    gunicorn app:app
    ```


<!-- ROADMAP -->
## Roadmap


- <del>Request handler</del>
- <del>Routing</del>
- <del>Class based view</del>
- <del>Unit tests</del>
- <del>CI</del>
- <del>Template support</del>
- <del>Custom exception handler</del>
- <del>Static files serving</del>
- <del>Middleware</del>
- <del>Custom response</del>
- <del>Pypi</del>
- <del>ORM</del>
- <del>CD</del>
- Authentication
- Demo app
- Cli
- Session and Cookies

<!-- CONTRIBUTING -->
## Contributing

Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.
