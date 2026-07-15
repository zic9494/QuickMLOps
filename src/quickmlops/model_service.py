from typing import Annotated, Any
from collections.abc import Callable
from annotated_doc import Doc
from functools import wraps

from quickmlops.adapter import ModelAdapter
from quickmlops.home_page import HomePage

class ModelService:
    def __init__(
        self,
        ml_model: Annotated[Any, Doc("")]
    ):
        self.user_model = ModelAdapter(ml_model)
        self.home_html = HomePage()

    def __getattr__(self, name):
        attribute = getattr(self.user_model, name)

        if callable(attribute):

            @wraps(attribute)
            def wrapper(*args, **kwargs):
                return attribute(*args, **kwargs)
            
            return wrapper
        
        return attribute

    def home_page(self)-> Callable[[], Any]:
        # TODO: 返回首頁的程式碼
        pass

    def perdict(self):
        return self.user_model.predict()
