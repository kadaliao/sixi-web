import inspect
from typing import Callable, Tuple, Dict, TypeVar, Any, Optional
from webob import Request, Response
from webob.exc import HTTPNotFound
from parse import parse

F = TypeVar("F", bound=Callable[..., Any])
VF_ARGS = TypeVar("VF_ARGS", bound=Tuple[Optional[Callable], Optional[Dict]])


class API:
    def __init__(self):
        self.routes = {}

    def __call__(self, environ, start_response):
        req = Request(environ)
        resp = self.despatch_request(req)
        return resp(environ, start_response)

    # def default_response(self, response):
    #     response.status_code = 404
    #     response.text = "Not found."

    def find_view_and_kwargs(self, path: str) -> VF_ARGS:
        """Find matching view function and parse parameters."""

        for rule, view_func in self.routes.items():
            result = parse(rule, path)
            if result is not None:
                return view_func, result.named
        return None, None

    def despatch_request(self, req: Request) -> Response:
        resp = Response()
        view_func, kwargs = self.find_view_and_kwargs(path=req.path)

        if view_func is not None:
            if inspect.isclass(view_func):
                view_func = getattr(view_func(), req.method.lower(), None)
                if not view_func:
                    raise AttributeError(f"Method not allowed: {req.method}")
            view_func(req, resp, **kwargs)
        else:
            return HTTPNotFound()

        return resp

    def route(self, rule: str) -> F:
        """Add route entrypoint."""

        view_func = self.routes.get(rule)
        if view_func:
            raise AssertionError(
                f"Cannot add route entry, conflict rule with `{view_func.__module__}.{view_func.__name__}`"
            )

        def decorator(view_func: F) -> F:
            self.routes[rule] = view_func
            return view_func

        return decorator
