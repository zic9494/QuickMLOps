from typing import Any

class ModelAdapter:
    def __init__(self, user_model: Any):
        self.user_model = user_model
        self.predict_kind = self._predict_kind()
        self.model_class = type(user_model)
        self.model_module = self.model_class.__module__
        self.model_qualname = self.model_class.__qualname__
        self.model_class_path = f"{self.model_module}.{self.model_qualname}"
        self.framework = self._detect_framework()

    def _predict_kind(self):
        if hasattr(self.user_model, "predict"):
            return "predict"

        if callable(self.user_model):
            return "callable"

        raise TypeError("The model must have predict() or be callable.")

    def _detect_framework(self):
        model_names = [
            cls.__module__
            for cls in type(self.user_model).__mro__
        ]

        framework_prefix = {
            "sklearn": "sklearn",
            "xgboost": "xgboost",
            "lightgbm": "lightgbm",
            "torch": "pytorch",
            "tensorflow": "tensorflow",
            "keras": "tensorflow",
        }

        for module_name in model_names:
            for prefix, framework in framework_prefix.items():
                if module_name == prefix or module_name.startswith(f"{prefix}."):
                    return framework

        return self.model_module.partition(".")[0]
    
    def predict(self, X: Any)-> Any:
        if self.predict_kind == "predict":
            return self.user_model.predict(X)
        
        if self.predict_kind == "callable":
            return self.user_model(X)
