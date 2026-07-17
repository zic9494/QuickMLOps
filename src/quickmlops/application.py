from typing import Annotated, Any, TypeVar, Awaitable
from collections.abc import Callable, Coroutine, Sequence
from pathlib import Path

from annotated_doc import Doc
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import Response, HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.routing import BaseRoute
from starlette.types import Lifespan, ASGIApp
from starlette.datastructures import State
from typing_extensions import deprecated

from quickmlops.model_service import ModelService
import quickmlops.routing as routing
from quickmlops.types_defs import DecoratedCallable
# Generalization and Prompting IDE
AppType = TypeVar("AppType", bound="QuickMLOps")
DEFAULT_STATIC_DIR = Path(__file__).parent / "static"


class QuickMLOps(Starlette):
    def __init__(
        self: AppType,
        ml_model: Annotated[
            Any,
            Doc("")
        ] = None,
        *,
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
        self.user_model = ModelService(ml_model=ml_model)
        self.debug = debug
        self.title = title
        self.root_path = root_path
        self.state: Annotated[State, Doc("")] = State()
        self.middleware_stack: ASGIApp | None = None

        self.user_middleware: list[Middleware] = (
            [] if middleware is None else list(middleware)
        )
        self.exception_handlers: dict[
            Any, Callable[[Request, Any], Response | Awaitable[Response]]
        ] = {} if exception_handlers is None else dict(exception_handlers)

        self.router: routing.APIRouter = routing.APIRouter(routes=routes)
    


    def deploy_home_page(self) -> None:

        def app() -> HTMLResponse:
            page = self.user_model.home_page()
            html_pages = HTMLResponse(page)
            return html_pages
        
        self.router.add_api_route("/", app, methods=["GET"])

    def _deploy_static_path(self) -> None:
        self.router.mount(
            "/static",
            StaticFiles(directory=DEFAULT_STATIC_DIR),
            name="static",
        )

    def include_router(self,
        router: Annotated[routing.APIRouter,Doc("")],
        *,
        prefix: Annotated[str, Doc("")] = ""
    )-> None:
        return self.router.include_router(router, prefix=prefix)

    def api_route(
        self,
        path: Annotated[str, Doc("")],
        *,
        methods: Annotated[list[str] | None, Doc("")] = None,
        name: Annotated[str | None, Doc("")] = None
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.api_route(path, methods=methods, name=name)

    def get(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.get(path, name=name)

    def options(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.options(path, name=name)

    def head(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.head(path, name=name)

    def post(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.post(path, name=name)

    def put(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.put(path, name=name)

    def delete(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.delete(path, name=name)

    def patch(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.patch(path, name=name)

    def trace(
        self,
        path: Annotated[str, Doc("")],
        name: Annotated[str | None, Doc("")] = None
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.trace(path, name=name)

