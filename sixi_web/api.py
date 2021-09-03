from webob import Request, Response


class API:
    def __init__(self):
        self.routes = {}

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def default_response(self, response):
        response = Response()
        response.status_code = 404
        response.text = "Not found."

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            if path == request_path:
                return handler

    def handle_request(self, request):
        response = Response()
        handler = self.find_handler(request_path=request.path)
        if handler is not None:
            handler(request, response)
        else:
            self.default_response(response)

        return response

    def route(self, path):
        def wrapper(handler):
            self.routes[path] = handler
            return handler

        return wrapper
