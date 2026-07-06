from typing import Annotated, Any, TypeVar, Awaitable
from annotated_doc import Doc
from typing_extensions import deprecated

from collections.abc import Callable, Coroutine, Sequence

from starlette import routing
from starlette.routing import BaseRoute
from starlette.types import ASGIApp

DecoratedCallable = TypeVar("DecoratedCallable", bound=Callable[..., Any])

class APIRoute(routing.Route):
    def __init__(self, path, endpoint, methods=None, name=None):
        super().__init__(
            path=path,
            endpoint=endpoint,
            methods=methods,
            name=name
        )

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
