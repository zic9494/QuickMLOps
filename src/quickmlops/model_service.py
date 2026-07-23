from typing import Annotated, Any
from collections.abc import Callable
from annotated_doc import Doc
from functools import wraps
from starlette.responses import HTMLResponse

from quickmlops.adapter import ModelAdapter
from quickmlops.home_page import HomePage

class ModelService:
    def __init__(
        self,
        ml_model: Annotated[Any, Doc("")],
        name: Annotated[str | None, Doc("")] = None,
        version: Annotated[str, Doc("")] = "1.0.0",
        stage: Annotated[str, Doc("")] = "production"
    ):
        self.user_model = self.user_model = ModelAdapter(ml_model)
        self.home_page = HomePage() # Only use at ModelService Standalone

        self.name = name
        self.version = version
        self.stage = stage

    def __getattr__(self, name):
        attribute = getattr(self.user_model, name)

        if callable(attribute):

            @wraps(attribute)
            def wrapper(*args, **kwargs):
                return attribute(*args, **kwargs)
            
            return wrapper
        
        return attribute

    def get_home_page(self)-> HTMLResponse:
        return HTMLResponse(self.home_page.get_page())

    def predict(self, X: Any):
        return self.user_model.predict(X)
