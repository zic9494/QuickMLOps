from typing import Annotated, Any, TypeVar, Awaitable
from collections.abc import Callable, Coroutine, Sequence

from annotated_doc import Doc
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import BaseRoute
from starlette.types import Lifespan
from typing_extensions import deprecated

from adapter import ModelAdapter
import routing 
# Generalization and Prompting IDE
AppType = TypeVar("AppType", bound="QuickMLOps")


class QuickMLOps(Starlette):
    def __init__(
        self: AppType,
        *,
        ml_model: Annotated[
            Any,
            Doc("")
        ],
        debug: Annotated[
            bool,
            Doc("")
        ] = False,
        routes: Annotated[
            list[BaseRoute] | None,
            Doc(""),
            deprecated("")
        ] = None,
        middleware: Annotated[
            Sequence[Middleware] | None,
            Doc("")
        ] = None,
        exception_handlers: Annotated[
            int | type[Exception],
            Callable[[Request, Any], Coroutine[Any, Any, Response]],
            Doc("")
        ] | None = None,
        lifespan: Annotated[
            Lifespan[AppType] | None,
            Doc("")
        ] | None = None,
        title: Annotated[
            str,
            Doc("")
        ] = "QuickMLOps",
        root_path: Annotated[
            str,
            Doc("")
        ] = ""
    ):
        self.ml_model = ModelAdapter(user_model=ml_model)
        self.debug = debug
        self.title = title
        self.root_path = root_path

        self.user_middleware: list[Middleware] = (
            [] if middleware is None else list(middleware)
        )
        self.exception_handlers: dict[
            Any, Callable[[Request, Any], Response | Awaitable[Response]]
        ] = {} if exception_handlers is None else dict(exception_handlers)

        self.router: routing.APIRouter = routing.APIRouter(routes=routes)

    def include_router()-> None:
        pass

