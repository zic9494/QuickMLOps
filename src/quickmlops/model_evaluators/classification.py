from dataclasses import dataclass
from collections.abc import Iterable
from numpy.typing import NDArray
from typing import Any, TypeAlias, Literal
import numpy as np
from numpy.typing import ArrayLike

from quickmlops.evaluation import BaseEvaluator

@dataclass(frozen=True)
class ClassificationData:
    y_true: NDArray[Any]
    y_pred: NDArray[Any]
    y_score: NDArray[Any] | None
    labels: NDArray[Any]

class ClassificationEvaluator(BaseEvaluator[ClassificationData]):
    task_type = "classification"

    def __init__(self) -> None:
        super().__init__()
        self.metrics = {
            "Confusion Matrix": self.confusion_matrix,
            "Accuracy": self.accuracy,
            "Precision": self.precision,
            "Recall": self.recall,
            "F1-Score": self.f1_score,
            "ROC-AUC": self.roc_auc,
        }
    
    def from_labels(
        self,
        target: ArrayLike,
        prediction: ArrayLike,
        labels: ArrayLike | None = None,
    ):
        y_true, y_pred = self._validate_inputs(target, prediction)
        y_score = None
        
        if labels is None:
            resolved_labels: NDArray[Any] =  np.unique(
                np.concatenate((y_true, y_pred))
            )
        else:
            resolved_labels = self._validate_labels(labels)
            self._validate_known_labels(y_true, resolved_labels, name="target")
            self._validate_known_labels(y_pred, resolved_labels, name="prediction")

        return ClassificationData(
            y_true=y_true,
            y_score=y_score,
            y_pred=y_pred,
            labels=resolved_labels
        )

    def from_probabilities(
        self,
        target: ArrayLike,
        probabilities: ArrayLike,
        *,
        positive_label: Any ,
        negative_label: Any ,
        threshold: float = 0.5,
        
    ):
        y_true, y_score = self._validate_inputs(target, probabilities)

        y_score = self._validate_probabilities(y_score)
        threshold = self._validate_threshold(threshold)

        if positive_label == negative_label:
            raise ValueError(
                "positive_label and negative_label must be different"
            )

        resolved_labels = np.asarray([
            negative_label,
            positive_label,
        ])

        if not np.all(np.isin(y_true, resolved_labels)):
            raise ValueError(
                "target contains labels other than "
                "positive_label and negative_label"
            )
        
        y_pred = np.where(
            y_score >= threshold,
            positive_label,
            negative_label,
        )

        return ClassificationData(
            y_true=y_true,
            y_score=y_score,
            y_pred=y_pred,
            labels=resolved_labels
        )

    
    def confusion_matrix(self, data: ClassificationData):
        pass

    def accuracy(self, data: ClassificationData):
        pass

    def precision(self, data: ClassificationData):
        pass

    def recall(self, data: ClassificationData):
        pass

    def f1_score(self, data: ClassificationData):
        pass

    def roc_auc(self, data: ClassificationData):
        pass
    
    def _validate_inputs(
        self,
        target: ArrayLike,
        prediction: ArrayLike,
    ) -> tuple[NDArray[Any], NDArray[Any]]:
        y_true = np.asarray(target)
        raw_prediction = np.asarray(prediction)

        if y_true.ndim != 1:
            raise ValueError("target must be one-dimensional")

        if raw_prediction.ndim != 1:
            raise ValueError("prediction must be one-dimensional")

        if y_true.size == 0:
            raise ValueError("target and prediction must not be empty")

        if y_true.size != raw_prediction.size:
            raise ValueError(
                "target and prediction must have the same length"
            )

        return y_true, raw_prediction
    
    def _validate_labels(self, labels: ArrayLike) -> NDArray[Any]:
            resolved_labels = np.asarray(labels)
    
            if resolved_labels.ndim != 1:
                raise ValueError("labels must be one-dimensional")
    
            if resolved_labels.size == 0:
                raise ValueError("labels must not be empty")
    
            if len(np.unique(resolved_labels)) != len(resolved_labels):
                raise ValueError("labels must not contain duplicates")
    
            return resolved_labels
    
    def _validate_known_labels(
        self,
        values: NDArray[Any],
        known_labels: NDArray[Any],
        *,
        name: str,
    ) -> None:
        if not np.all(np.isin(values, known_labels)):
            raise ValueError(f"{name} contains unknown labels")

    def _validate_probabilities(
        self,
        probabilities: NDArray[Any],
    ) -> NDArray[np.float64]:
        try:
            probabilities = probabilities.astype(np.float64)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "probabilities must contain numeric values"
            ) from exc

        if not np.all(np.isfinite(probabilities)):
            raise ValueError(
                "probabilities must contain only finite values"
            )

        if np.any((probabilities < 0.0) | (probabilities > 1.0)):
            raise ValueError(
                "probabilities must be between 0 and 1"
            )

        return probabilities

    def _validate_threshold(self, threshold: float) -> float:
        try:
            threshold = float(threshold)
        except (TypeError, ValueError) as exc:
            raise ValueError("threshold must be numeric") from exc

        if not np.isfinite(threshold):
            raise ValueError("threshold must be finite")

        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")

        return threshold




    
