from sixi_web.api import API

app = API()


@app.route("/home")
def home(request, response):
    response.text = "Hello world, mother fucker"


@app.route("/about")
def about(request, response):
    response.text = "一只菜狗四喜"
