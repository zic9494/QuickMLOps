from typing import Annotated, Any, TypeVar, Awaitable, TypeAlias, Literal
from collections.abc import Callable, Coroutine, Sequence


DecoratedCallable = TypeVar("DecoratedCallable", bound=Callable[..., Any])
TaskType: TypeAlias = Literal[
    "classification",
    "regression",
    "clustering",
    "unknown",
]