"""Sixi web framework - API class."""
import inspect
import os
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

from jinja2 import Environment, FileSystemLoader
from parse import parse
from requests import Session as RequestsSession
from webob import Request, Response
from webob.exc import HTTPNotFound
from whitenoise import WhiteNoise
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter

from .middleware import Middleware

F = TypeVar("F", bound=Callable[..., Any])
VF_ARGS = TypeVar("VF_ARGS", bound=Tuple[Optional[Callable], Optional[Dict]])


class API:
    def __init__(self, templates_dir=None, static_dir=None):
        self.routes = {}
        self.error_handlers = {}
        self.templates_env = None
        self.whitenoise = None

        if templates_dir:
            self.templates_env = Environment(loader=FileSystemLoader(os.path.abspath(templates_dir)), autoescape=True)
        if static_dir:
            self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)

        self.middleware = Middleware(self)

    def __call__(self, environ, start_response):
        path_info = environ["PATH_INFO"]
        if self.whitenoise and path_info.startswith("/static"):
            environ["PATH_INFO"] = path_info[len("/static") :]
            return self.whitenoise(environ, start_response)

        return self.middleware(environ, start_response)

    def wsgi_app(self, environ, start_response):
        req = Request(environ)
        resp = self.despatch_request(req)
        return resp(environ, start_response)

    # def default_response(self, response):
    #     response.status_code = 404
    #     response.text = "Not found."

    def find_view_and_kwargs(self, path: str) -> VF_ARGS:
        """Find matching view function and parse parameters."""

        for rule, view_func_data in self.routes.items():
            result = parse(rule, path)
            if result is not None:
                return view_func_data, result.named
        return None, None

    def despatch_request(self, req: Request) -> Response:
        resp = Response()
        view_func_data, kwargs = self.find_view_and_kwargs(path=req.path)

        if view_func_data is not None:

            view_func = view_func_data["view_func"]
            allowed_methods = view_func_data["allowed_methods"]
            if inspect.isclass(view_func):
                view_func = getattr(view_func(), req.method.lower(), None)
                if not view_func:
                    raise AttributeError(f"Method not allowed: {req.method}")
            else:
                if req.method.lower() not in allowed_methods:
                    raise AttributeError(f"Method not allowed: {req.method}")

            try:
                view_func(req, resp, **kwargs)
            except Exception as e:
                error_handler = self.error_handlers.get(e.__class__)
                if error_handler:
                    error_handler(req, resp, e)
                else:
                    raise e

        else:
            return HTTPNotFound()

        return resp

    def add_route(self, rule: str, view_func: F, allowed_methods: List[str] = None) -> None:
        """Add route entrypoint."""
        _existed_view_func_data = self.routes.get(rule)
        if _existed_view_func_data:
            _existed_view_func = _existed_view_func_data["view_func"]
            msg = f"Cannot add route entry: {rule}, conflict rules \n- {_existed_view_func.__module__}.{_existed_view_func.__name__}"
            msg += f"\n- {view_func.__module__}.{view_func.__name__}"
            raise AssertionError(msg)
        if allowed_methods is None and inspect.isfunction(view_func):
            allowed_methods = "get post put patch delete options".split()
        self.routes[rule] = {"view_func": view_func, "allowed_methods": allowed_methods}

    def route(self, rule: str, allowed_methods: List[str] = None) -> F:
        """Add route entrypoint."""

        def decorator(view_func: F) -> F:
            self.add_route(rule, view_func, allowed_methods)
            return view_func

        return decorator

    def test_client(self):
        base_url = "http://sixi-web"
        adapter = RequestsWSGIAdapter(self)

        class TestClient:
            def __init__(self):
                self.session = RequestsSession()
                self.session.mount(prefix=base_url, adapter=adapter)

            def get(self, url, *args, **kwargs):
                return self.session.get(base_url + url, *args, **kwargs)

            def post(self, url, *args, **kwargs):
                return self.session.post(base_url + url, *args, **kwargs)

            def head(self, url, *args, **kwargs):
                return self.session.head(base_url + url, *args, **kwargs)

            def put(self, url, *args, **kwargs):
                return self.session.put(base_url + url, *args, **kwargs)

            def options(self, url, *args, **kwargs):
                return self.session.options(base_url + url, *args, **kwargs)

            def delete(self, url, *args, **kwargs):
                return self.session.delete(base_url + url, *args, **kwargs)

        return TestClient()

    def template(self, template_name: str, context: Dict = None):
        if not self.templates_env:
            raise AttributeError("API instance initiated with no templates_dir.")
        if context is None:
            context = {}
        return self.templates_env.get_template(template_name).render(**context)

    def add_error_handler(self, exception_cls: type, error_handler: F) -> None:
        _existed_error_handler = self.error_handlers.get(exception_cls)
        if _existed_error_handler:
            msg = f"Cannot add error handler for : {exception_cls}, conflict handlers:\n- {_existed_error_handler.__module__}.{_existed_error_handler.__name__}"
            msg += f"\n- {error_handler.__module__}.{error_handler.__name__}"
            raise AssertionError(msg)
        self.error_handlers[exception_cls] = error_handler

    def error_handler(self, exception_cls: type) -> F:
        def decorator(error_handler: F) -> F:
            self.add_error_handler(exception_cls, error_handler)
            return error_handler

        return decorator

    def add_middleware(self, middleware_cls):
        self.middleware.add(middleware_cls)
