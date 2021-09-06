from sixi_web import API

app = API(templates_dir="templates", static_dir="static")


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


@app.route("/")
@app.route("/html")
def html(req, resp):
    resp.text = app.template("index.html", context=dict(title="hi", name="kada"))


@app.error_handler(AttributeError)
def attribute_handler(req, resp, e):
    print(e)
