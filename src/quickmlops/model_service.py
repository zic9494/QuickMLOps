from typing import Annotated, Any
from collections.abc import Callable
from annotated_doc import Doc

from quickmlops.adapter import ModelAdapter

class ModelService:
    def __init__(
        self,
        *,
        ml_model: Annotated[Any, Doc("")] = None
    ):
        self.user_model = None if ml_model is None else ModelAdapter(ml_model)

    def home_page()-> Callable[[], Any]:
        pass

    def perdict():
        pass
