from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray, ArrayLike
from typing import Any

from quickmlops.model_evaluators.base_evaluator import BaseEvaluator


@dataclass(frozen=True)
class RegressionData:
    target: NDArray[np.float64]
    prediction: NDArray[np.float64]

class RegressionEvaluator(BaseEvaluator[RegressionData]):
    task_type = "regression"

    def __init__(self) -> None:
        super().__init__()
        self.metrics = {
            "MAE": self.mae,
            "MSE": self.mse,
            "RMSE": self.rmse,
            "R^2": self.r2,
        }

    def from_predictions(
        self,
        target: ArrayLike,
        prediction: ArrayLike
    ) -> RegressionData:
        y_true, y_pred = self._validate_input(target, prediction)

        return RegressionData(
            target=y_true,
            prediction=y_pred
        )

    def mae(self, data: RegressionData) -> float:
        return float(np.mean(np.abs(data.target - data.prediction)))

    def mse(self, data: RegressionData) -> float:
        return float(np.mean((data.target - data.prediction)**2))

    def rmse(self, data: RegressionData) -> float:
        return float(np.sqrt(self.mse(data)))

    def r2(self, data: RegressionData) -> float:
        residual_sum = np.sum((data.target - data.prediction)**2)
        total_sum = np.sum((data.target - np.mean(data.target))**2)
        return (1.0 - float(residual_sum / total_sum))

    def _validate_input(
        self,
        target: ArrayLike,
        prediction: ArrayLike,       
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        try:
            y_true = np.asarray(target, dtype=np.float64)
            y_pred = np.asarray(prediction, dtype=np.float64)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "target and prediction must contain numeric values"
            ) from exc

        if not np.all(np.isfinite(y_true)):
            raise ValueError("target must contain only finite values")

        if not np.all(np.isfinite(y_pred)):
            raise ValueError("prediction must contain only finite values")
        
        if y_true.ndim!= 1:
            raise ValueError("target must be one-dimensional")

        if y_pred.ndim != 1:
            raise ValueError("prediction must be one-dimensional")

        if y_true.size == 0:
            raise ValueError("target and prediction must not be empty")

        if y_true.size != y_pred.size:
            raise ValueError(
                "target and prediction must have the same length"
            )

        return y_true, y_pred