from sixi_web import API

app = API()


@app.route("/")
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
