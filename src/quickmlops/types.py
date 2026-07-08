from typing import Annotated, Any, TypeVar, Awaitable
from collections.abc import Callable, Coroutine, Sequence


DecoratedCallable = TypeVar("DecoratedCallable", bound=Callable[..., Any])
