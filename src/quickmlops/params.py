from typing import Any, get_args, get_origin, Annotated, Union
from types import UnionType
from inspect import Parameter

from starlette.requests import Request
from starlette.responses import Response

class Param:
    source: str

    def __init__(
        self,
        default: Any = Parameter.empty,
        alias: str | None = None
    ):
        self.default = default
        self.alias = alias

class Path(Param):
    source = "path"


class Query(Param):
    source = "query"


class Header(Param):
    source = "header"


class Cookie(Param):
    source = "cookie"

def _get_params_value(
    request: Request,
    response: Response,
    name: str,
    annotation: Any,
    default: Any
) -> Any:
    real_type, marker = _unwarp_annotated(annotation)

    if real_type is Request:
        return request
    
    if real_type is Response:
        return response

    if marker is None:
        if name == "request":
            return request
        
        if name in request.path_params:
            marker = Path()
        else:
            marker = Query()

    alias = marker.alias or name

    match marker.source:
        case "path":
            values = request.path_params
        case "query":
            values = request.query_params
        case "header":
            values = request.headers
        case "cookie":
            values = request.cookies

    value = values.get(alias)

    if value is None:
        if marker.default is not Parameter.empty:
            return marker.default

        if default is not Parameter.empty:
            return default
        
        raise ValueError(f"Missing required parameter: {alias}")

    return _convert_value(value, real_type)


def _unwarp_annotated(annotation: Any) -> tuple[Any, Param | None]:
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        real_type = args[0]

        for meta in args[1:]:
            if isinstance(meta, Param):
                return real_type, meta
            
        return None
    return annotation, None
    
def _convert_value(value: Any, annotation: Any) -> Any:
    if annotation is Parameter.empty or value is None:
        return value
    
    annotation = _strip_optional(annotation)

    if annotation is bool:
        if isinstance(value, bool):
            return value
        
        value = str(value).lower()
        if value in {"1", "true", "yes", "on"}:
            return True
        if value in {"0", "false", "no", "off"}:
            return False
        
        raise ValueError(f"Invalid boolean value: {value}")

    if annotation in {str, int, float}:
        return annotation(value)

    return value

# NOTICE: only returns the first type that is not NoneType.
def _strip_optional(annotation: Any) -> Any:
    if _is_optional(annotation):
        return next(arg for arg in get_args(annotation) if arg is not type(None))
    return annotation

def _is_optional(annotation: Any) -> Any:
    origin = get_origin(annotation)
    if origin in (Union, UnionType):
        return type(None) in get_args(annotation)
    return False