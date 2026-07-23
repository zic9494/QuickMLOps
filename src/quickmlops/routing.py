import json
from inspect import isawaitable, signature
from annotated_doc import Doc
from typing_extensions import deprecated
from typing import Annotated, Any, TypeVar, Awaitable
from collections.abc import Callable, Coroutine, Sequence
from copy import copy

from starlette import routing
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import BaseRoute
from starlette.types import ASGIApp, Scope, Receive, Send

from quickmlops.types_defs import DecoratedCallable
from quickmlops.params import _get_params_value

def request_response(func: Callable[[Request], Awaitable[Response] | Response]) -> ASGIApp:
    async def app(scope: Scope, receive: Receive, send: Send):
        request = Request(scope, receive=receive)
        response = func(request)

        if isawaitable(response):
            response = await response

        await response(scope, receive, send)

    return app

def _clone_route_with_prefix(
    route: BaseRoute,
    prefix: str,
) -> BaseRoute:
    if isinstance(route, routing.Mount):
        return routing.Mount(
            path=prefix + route.path,
            app=route.app,
            name=route.name,
        )

    if not isinstance(route, (routing.Route, routing.WebSocketRoute)):
        raise TypeError(
            f"Cannot apply path prefix to {type(route).__name__}"
        )

    cloned_route = copy(route)
    cloned_route.path = prefix + route.path

    (
        cloned_route.path_regex,
        cloned_route.path_format,
        cloned_route.param_convertors,
    ) = routing.compile_path(cloned_route.path)

    return cloned_route

class APIRoute(routing.Route):
    def __init__(self, path, endpoint, methods=None, name=None):
        super().__init__(
            path=path,
            endpoint=endpoint,
            methods=methods,
            name=name
        )
        self.app = request_response(self.get_route_handler())

    def matches(self, scope: Scope):
        return super().matches(scope)
    
    def handle(self, scope: Scope, receive: Receive, send: Send):
        return super().handle(scope, receive, send)
    
    def get_route_handler(self) -> Callable[[Request], dict[str, Any] | Response | Any]:
        endpoint = self.endpoint
        dependant = signature(endpoint)

        async def app(request: Request) -> Response:
            kwargs = {}
            temp_response = Response()
            try:
                for param in dependant.parameters.values():
                    kwargs[param.name] = _get_params_value(
                        request=request,
                        response=temp_response,
                        name=param.name,
                        annotation= param.annotation,
                        default=param.default
                    )
            except ValueError as exc:
                return JSONResponse(
                    {"detail": str(exc)},
                    status_code=422,
                )
            result = endpoint(**kwargs)

            if isawaitable(result):
                result = await result
            
            if isinstance(result, Response):
                return result

            if isinstance(result, dict):
                content = json.dumps(result)
            else :
                content = json.dumps({'detail':str(result)})
            
            final_response = Response(
                content,
                status_code=temp_response.status_code,
                media_type="application/json",
            )

            excluded_headers = {b"content-length", b"content-type"}

            final_response.raw_headers.extend(
                (key, value)
                for key, value in temp_response.raw_headers
                if key.lower() not in excluded_headers
            )

            return final_response
        
        return app


class APIRouter(routing.Router):
    def __init__(
        self,
        *,
        prefix: Annotated[str, Doc("")] = "",
        routes: Annotated[list[BaseRoute] | None, Doc(""), deprecated("")] = None,
        redirect_slashes: Annotated[bool, Doc("")] =True,
        default: Annotated[ASGIApp | None, Doc("")] = None,
        route_class: Annotated[type[APIRoute],Doc("")] = APIRoute,
        deprecated: Annotated[bool | None,Doc("")] = None
    ):
        super().__init__(
            routes=routes,
            redirect_slashes=redirect_slashes,
            default=default
        )

        # prefix check
        if prefix:
            assert prefix.startswith("/")
            assert not prefix.endswith("/")

        # Router setting
        self.prefix = prefix
        self.route_class = route_class

        #other
        self.deprecated = deprecated
        self._routes_version = 0
        # self._frontend_routes: _FrontendRouteGroup | None = None
        
    # add new route into starlette.route
    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any], # Any kind of callable object
        *,
        methods: set[str] | list[str] | None = None,
        name: str | None = None
    ) -> None:
        
        assert path.startswith('/')

        route = self.route_class(
            self.prefix + path,
            endpoint,
            methods=methods,
            name=name
        )
        self.routes.append(route)
        self._mark_route_changed()

    # Decorator
    def api_route(
        self,
        path: str,
        *,
        methods: list[str] | None = None,
        name: str | None = None
    )-> Callable[[DecoratedCallable], DecoratedCallable]:
        
        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.add_api_route(
                path,
                func,
                methods=methods,
                name=name
            )
            return func
        
        return decorator

    def include_router(
        self,
        router: Annotated["APIRouter", Doc("")],
        *,
        prefix: Annotated[str, Doc("")] = ""
    ) -> None:
        if prefix:
            assert prefix.startswith("/"), "A path prefix must start with '/'"
            assert not prefix.endswith("/"), (
                "A path prefix must not end with '/', as the routes will start with '/'"
            )

        for route in router.routes:
            self.routes.append(
                _clone_route_with_prefix(route, prefix)
            )
        self._mark_route_changed()


    def get(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    )->Callable[[DecoratedCallable], DecoratedCallable]:
        return self.api_route(
            path,
            name=name,
            methods=["GET"]
        )

    def options(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    )->Callable[[DecoratedCallable], DecoratedCallable]:
        return self.api_route(
            path,
            name=name,
            methods=["OPTIONS"]
        )

    def head(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    )->Callable[[DecoratedCallable], DecoratedCallable]:
        return self.api_route(
            path,
            name=name,
            methods=["HEAD"]
        )

    def post(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    )->Callable[[DecoratedCallable], DecoratedCallable]:
        return self.api_route(
            path,
            name=name,
            methods=["POST"]
        )

    def put(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    )->Callable[[DecoratedCallable], DecoratedCallable]:
        return self.api_route(
            path,
            name=name,
            methods=["PUT"]
        )

    def delete(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    )->Callable[[DecoratedCallable], DecoratedCallable]:
        return self.api_route(
            path,
            name=name,
            methods=["DELETE"]
        )

    def patch(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    )->Callable[[DecoratedCallable], DecoratedCallable]:
        return self.api_route(
            path,
            name=name,
            methods=["PATCH"]
        )

    def trace(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    )->Callable[[DecoratedCallable], DecoratedCallable]:
        return self.api_route(
            path,
            name=name,
            methods=["TRACE"]
        )

    def _mark_route_changed(self) -> None:
        self._routes_version += 1
