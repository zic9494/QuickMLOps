from typing import Annotated, Any, TypeVar, Awaitable, List, Mapping
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
from quickmlops.home_page import HomePage
import quickmlops.routing as routing
from quickmlops.types_defs import DecoratedCallable
from quickmlops.constants import DEFAULT_STATIC_DIR, DEFAULT_STATIC_URL
# Generalization and Prompting IDE
AppType = TypeVar("AppType", bound="QuickMLOps")

class QuickMLOps(Starlette):
    def __init__(
        self: AppType,
        ml_model: Annotated[
            Any | None ,
            Doc("")
        ] = None,
        *,
        ml_models: Annotated[
            List[Any] | Mapping[str, Any] | None ,
            Doc("")
        ] = None,
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
        self.user_models: List[ModelService] = []
        self.home_page = HomePage()
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

        if ml_model is not None:
            self.include_model(ml_model)
        
        if isinstance(ml_models, dict):
            for name, model in ml_models.items():
                self.include_model(model, name=name)

        elif ml_models is not None:
            for model in ml_models:
                self.include_model(model)

        
        self._model_index = 0
        self._model_table = []
        self.router: routing.APIRouter = routing.APIRouter(routes=routes)

    def deploy_home_page(self) -> None:
        def app() -> HTMLResponse:
            page = self.home_page.get_page()
            html_pages = HTMLResponse(page)
            return html_pages
        
        self._deploy_static_path()
        self.router.add_api_route("/", app, methods=["GET"])

    def include_model(
        self,
        user_model: Annotated[Any, Doc('')],
        *,
        name: Annotated[str | None, Doc("")] = None,
        version: Annotated[str | None, Doc("")] = "1.0.0"
    ) -> None:
        
        model_servive = ModelService(
            user_model,
            name=name,
            version=version
        )
        self.user_models.append(model_servive)
        self._deploy_model_route()
        
    def include_router(self,
        router: Annotated[routing.APIRouter,Doc("")],
        *,
        prefix: Annotated[str, Doc("")] = ""
    )-> None:
        self.router.include_router(router, prefix=prefix)

    def api_route(
        self,
        path: Annotated[str, Doc("")],
        *,
        methods: Annotated[list[str] | None, Doc("")] = None,
        name: Annotated[str | None, Doc("")] = None
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        return self.router.api_route(path, methods=methods, name=name)

    def _deploy_static_path(self) -> None:
        self.router.mount(
            DEFAULT_STATIC_URL,
            StaticFiles(directory=DEFAULT_STATIC_DIR),
            name="default_home_page_static",
        )

    def _deploy_model_route(self, name: str | None = None) -> None:
        path = "/models/"
        if name is not None:
            path += name
        else:
            path += str(self._model_index)

        marker = {
            "model_index": self._model_index,
            "name": name,
            "path": path
        }
        self._model_table.append(marker)

        async def predict(request: Request):
            data = await request.json()
            model_id = data["model_id"]
            user_model = self.user_models[model_id]
            return user_model.perdict(data["predict"])

        self.router.add_api_route(path+"/predict", predict, methods=["POST"], name=(name or ("model" + str(self._model_index))))
        self._model_index += 1

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
