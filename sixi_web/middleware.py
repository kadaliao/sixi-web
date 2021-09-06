"""Sixi webframework - Middleware class."""
from webob import Request


class Middleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        req = Request(environ)
        resp = self.app.despatch_request(req)
        return resp(environ, start_response)

    def add(self, middleware_cls):
        self.app = middleware_cls(self.app)

    def process_request(self, req):
        pass

    def process_response(self, req, resp):
        pass

    def despatch_request(self, req):
        self.process_request(req)
        resp = self.app.despatch_request(req)
        self.process_response(req, resp)

        return resp
