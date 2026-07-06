from typing import Annotated, Any, TypeVar, Awaitable
from annotated_doc import Doc
from typing_extensions import deprecated

from starlette import routing
from starlette.routing import BaseRoute
from starlette.types import ASGIApp

class APIRoute(routing.Route):
    def __init__(self, path, endpoint, *, methods = None, name = None, include_in_schema = True, middleware = None):
        super().__init__(path, endpoint, methods=methods, name=name, include_in_schema=include_in_schema, middleware=middleware)
        pass


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
        # self._frontend_routes: _FrontendRouteGroup | None = None
        


