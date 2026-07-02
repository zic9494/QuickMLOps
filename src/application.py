from typing import TypeVar, Annotated

from starlette.applications import Starlette 
from starlette.routing import BaseRoute

from annotated_doc import Doc
from typing_extensions import deprecated

# Generalization and Prompting IDE
AddType = TypeVar("AppType", bound="QuickMLOps")

class QuickMLOps(Starlette):
    def __init__(
            self: AddType,
            debug: Annotated[
                bool,
                Doc()
            ] = False,
            routes: Annotated[
                list[BaseRoute] | None,
                Doc(),
                deprecated()
            ] = None,
            title: Annotated[
                str,
                Doc()
            ] = "QuickMLOps"

        ):
        pass