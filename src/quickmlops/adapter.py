class ModelAdapter:
    def __init__(self, user_model):
        self.user_model = user_model
        self.framework = self._detect_framework()
        self.predict_kind = self._predict_kind()

    def _predict_kind(self):
        if hasattr(self.user_model, "predict"):
            return "predict"

        if callable(self.user_model):
            return "callable"

        raise TypeError("The model must have predict() or be callable.")

    def _detect_framework(self):
        module_name = type(self.user_model).__module__  #NOTICE

        if module_name.startswith("sklearn"):
            return "sklearn"

        if module_name.startswith("xgboost"):
            return "xgboost"

        if module_name.startswith("lightgbm"):
            return "lightgbm"

        if module_name.startswith("torch"):
            return "pytorch"

        if module_name.startswith("tensorflow") or module_name.startswith("keras"):
            return "tensorflow"


        raise TypeError("Unsupported model type")