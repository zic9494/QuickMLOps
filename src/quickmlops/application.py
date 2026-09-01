from typing import Annotated, Any, TypeVar, Awaitable, List, Mapping, Dict
from collections.abc import Callable, Coroutine, Sequence
from pathlib import Path
from re import fullmatch
from inspect import isawaitable
from json import JSONDecodeError

from annotated_doc import Doc
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import Response, HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.routing import BaseRoute
from starlette.types import Lifespan, ASGIApp
from starlette.datastructures import State
from starlette.concurrency import run_in_threadpool
from typing_extensions import deprecated

from quickmlops.model_service import ModelService
from quickmlops.adapter import TaskType
from quickmlops.home_page import HomePage
import quickmlops.routing as routing
from quickmlops.types_defs import DecoratedCallable
from quickmlops.constants import DEFAULT_STATIC_DIR, DEFAULT_STATIC_URL, DEFAULT_MODEL_LISTING_URL
# Generalization and Prompting IDE
AppType = TypeVar("AppType", bound="QuickMLOps")

class QuickMLOps(Starlette):
    def __init__(
        self: AppType,
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
            Mapping[
                int | type[Exception],
                Callable[[Request, Any], Response | Awaitable[Response]],
            ] | None,
            Callable[[Request, Any], Coroutine[Any, Any, Response]],
            Doc("")
        ] | None = None,

        # TODO
        # lifespan: Annotated[
        #     Lifespan[AppType] | None,
        #     Doc("")
        # ] | None = None,
        
        title: Annotated[
            str,
            Doc("")
        ] = "QuickMLOps",
        root_path: Annotated[
            str,
            Doc("")
        ] = ""
    ):
        self._model_index = 0
        self.user_models: Dict[int, ModelService] = {}
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

        self.router: routing.APIRouter = routing.APIRouter(routes=routes)
        
    def deploy_home_page(self) -> None:
        def app() -> HTMLResponse:
            page = self.home_page.get_page()
            html_pages = HTMLResponse(page)
            return html_pages
        
        self._deploy_static_path()
        self._deploy_model_listing()
        self.router.add_api_route("/", app, methods=["GET"])

    def include_model(
        self,
        user_model: Annotated[Any, Doc('')],
        task_type: Annotated[TaskType, Doc("")],
        *,
        name: Annotated[str | None, Doc("")] = None,
        path: str = "/model",
        version: Annotated[str, Doc("")] = "1.0.0",
        expose_predict: bool = True,
    ) -> None:

        model_service = ModelService(
            user_model,
            task_type=task_type,
            name=name,
            version=version
        )

        self.include_model_service(
            model_service,
            path=path,
            expose_predict=expose_predict
        )

    def include_model_service(
        self,
        service: ModelService,
        *,
        path: str = "/model",
        expose_predict: bool = True,
    ) -> None:

        if not isinstance(service, ModelService):
            raise TypeError("service must be an instance of ModelService")

        if not isinstance(path, str) or not path.startswith("/"):
            raise ValueError("Model path must start with '/'")

        if path != "/" and "//" in path:
            raise ValueError("Model path cannot contain consecutive slashes")

        if path == "/":
            path = ""
        else:
            path = path.rstrip("/")
        
        self._validate_model_name(service.name)
        
        model_id = self._model_index
        routes = (
            self._create_predict_route(path, model_id, service.name)
            if expose_predict
            else []
        )
        
        self._commit_model_registration(
            model_id = model_id,
            model_service= service,
            routes = routes
        )

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

    def _deploy_model_listing(self) -> None:
        def listing():
            result = []

            for model_id, model in self.user_models.items():
                data = {
                    "model_id": model_id,
                    "model_name": model.name,
                    "model_version": model.version,
                    "model_module":model.model_module,
                    "model_qualname":model.model_qualname,
                    "model_class_path":model.model_class_path,
                    "task_type":model.task_type,
                }
                result.append(data)
            return {"detail": result}
        
        self.router.add_api_route(DEFAULT_MODEL_LISTING_URL, listing, methods=["GET"], name="model_listing")

    def _get_route(self, path:str, endpoint: Any, methods: List[str],name: str | None = None) -> BaseRoute:
        return self.router.route_class(
            path = path,
            endpoint=endpoint,
            methods=methods,
            name=name
        )
    
    def _create_predict_route(self, path: str, model_id: int, name: str | None) -> List[BaseRoute]:

        endpoint = self._create_predict_endpoint(model_id)

        self._validate_route_path(path + f"/{model_id}/predict", ["POST"])
        routes = [self._get_route(
            path + f"/{model_id}/predict", 
            endpoint, 
            ["POST"], 
            f"model{model_id}"
        )]

        if name is not None:
            self._validate_route_path(path + f"/{name}/predict", ["POST"])
            routes.append(
                self._get_route(
                    path + f"/{name}/predict", 
                    endpoint, 
                    ["POST"], 
                    name
                )
            )

        return routes

    def _create_predict_endpoint(self, model_id: int):

        async def predict(request: Request):
            data = await self._validate_predict_endpoint_request(request)

            if isinstance(data, JSONResponse):
                return data

            user_model = self.user_models[model_id]
            result = await run_in_threadpool(
                user_model.predict,
                data["predict"]
            )

            if isawaitable(result):
                result = await result
            return result

        return predict

    def _commit_model_registration(
        self,
        *,
        model_id: int,
        model_service: ModelService,
        routes: List[BaseRoute]
    ) -> None:
        
        if model_id in self.user_models:
            raise RuntimeError(f"Model ID already exists: {model_id}")
        
        model_added = False
        added_routes: List[BaseRoute] = []

        try:
            self.user_models[model_id] = model_service
            model_added = True

            for route in routes:
                self.router.routes.append(route)
                added_routes.append(route)
            self.router._mark_route_changed()

            self._model_index += 1

        except Exception:
            for route in reversed(added_routes):
                self.router.routes.remove(route)

            if added_routes:
                self.router._mark_route_changed()

            if model_added:
                self.user_models.pop(model_id, None)

            raise

    def _validate_model_name(self, name: str | None) -> None:
        if name is None:
            return None

        if not fullmatch(r"^(?=.*[A-Za-z_-])[A-Za-z0-9][A-Za-z0-9_-]*$", name):
            raise ValueError(
                "Model name must start with an alphanumeric character "
                "contain only letters, numbers, hyphens, or underscores, "
                "and not consist entirely of numbers."
            )

        if any(model.name == name for model in self.user_models.values()):
            raise ValueError(f"Model name already exists {name}")

    def _validate_route_path(
        self, 
        path: str,
        methods: List[str] | set[str]
    ) -> None:
        requested_methods = {method.upper() for method in methods}

        for route in self.router.routes:
            if getattr(route, "path", None) != path:
                continue

            existing_methods: set[str] = getattr(route, "methods", set()) or set()

            if requested_methods & existing_methods:
                raise ValueError(
                    f"Route already used: {path} "
                    f"for methods {sorted(requested_methods & existing_methods)}"
                )

    async def _validate_predict_endpoint_request(self, request: Request) -> dict | JSONResponse:
        try:
            data = await request.json()
        except JSONDecodeError:
            return JSONResponse(
                {"detail": "Request body must be valid JSON"},
                status_code=400,
            )

        if not isinstance(data, dict) or "predict" not in data:
            return JSONResponse(
                {"detail": "Missing required field: predict"},
                status_code=422,
            )

        return data
            
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
