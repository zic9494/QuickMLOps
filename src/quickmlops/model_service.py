from typing import Annotated, Any
from collections.abc import Callable
from annotated_doc import Doc
from functools import wraps

from quickmlops.adapter import ModelAdapter
from quickmlops.home_page import HomePage

class ModelService:
    def __init__(
        self,
        ml_model: Annotated[Any, Doc("")] = None
    ):
        self.user_model = self.user_model = ModelAdapter(ml_model) if ml_model is not None else None
        self.home_page = HomePage()

    def __getattr__(self, name):
        attribute = getattr(self.user_model, name)

        if callable(attribute):

            @wraps(attribute)
            def wrapper(*args, **kwargs):
                return attribute(*args, **kwargs)
            
            return wrapper
        
        return attribute

    def get_home_page(self)-> str:
       return self.home_page.get_page()

    def perdict(self):
        return self.user_model.predict()
