from typing import Annotated, Any, List
from collections.abc import Callable
from annotated_doc import Doc
from functools import wraps

from quickmlops.adapter import ModelAdapter, TaskType

class ModelService:
    def __init__(
        self,
        ml_model: Annotated[Any, Doc("")],
        *,
        task_type: Annotated[TaskType, Doc("")] = "unknown",
        name: Annotated[str | None, Doc("")] = None,
        version: Annotated[str, Doc("")] = "1.0.0",
        stage: Annotated[str, Doc("")] = "production",
        descript: Annotated[str | None, Doc("")] = None,
        tags: Annotated[List[str] | None, Doc("")] = None
    ):
        self.user_model = ModelAdapter(ml_model, task_type)

        self.name = name
        self.version = version
        self.stage = stage
        self.descript = descript
        self.tags = tags

    def __getattr__(self, name):
        attribute = getattr(self.user_model, name)

        if callable(attribute):

            @wraps(attribute)
            def wrapper(*args, **kwargs):
                return attribute(*args, **kwargs)
            
            return wrapper
        
        return attribute

    def predict(self, X: Any):
        return self.user_model.predict(X)
