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


@app.route("/task")
class Task:
    def get(self, req, resp):
        resp.text = "Get a task"

    def post(self, req, resp):
        resp.text = "Create a task"


@app.route("/html")
def html(req, resp):
    resp.html = app.template("index.html", context=dict(title="some title", name="some name"))


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
