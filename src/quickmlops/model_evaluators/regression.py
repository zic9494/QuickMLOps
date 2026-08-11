from quickmlops.evaluation import BaseEvaluator

class RegressionEvaluator(BaseEvaluator):
    task_type = "regression"

    def __init__(self) -> None:
        super().__init__()
        self.metrics = {
            "MAE": self.mae,
            "MSE": self.mse,
            "RMSE": self.rmse,
            "R^2": self.r2,
        }

    def mae(self, y_true, y_pred, **kwargs):
        pass

    def mse(self, y_true, y_pred, **kwargs):
        pass

    def rmse(self, y_true, y_pred, **kwargs):
        pass

    def r2(self, y_true, y_pred, **kwargs):
        pass
