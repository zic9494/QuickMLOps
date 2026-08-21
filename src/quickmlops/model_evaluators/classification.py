from dataclasses import dataclass
from collections.abc import Iterable
from numpy.typing import NDArray
from typing import Any, TypeAlias, Literal, Dict, List
import numpy as np
from numpy.typing import ArrayLike

from quickmlops.evaluation import BaseEvaluator

ClassificationType: TypeAlias = Literal["binary", "multiclass"]

@dataclass(frozen=True)
class ClassificationData:
    y_true: NDArray[Any]
    y_pred: NDArray[Any]
    y_score: NDArray[np.float64] | None
    labels: NDArray[Any]
    kind: ClassificationType

class ClassificationEvaluator(BaseEvaluator[ClassificationData]):
    task_type = "classification"

    def __init__(self) -> None:
        super().__init__()
        self.metrics = {
            "Confusion Matrix": self.confusion_matrix,
            "Accuracy": self.accuracy,
            "Precision": self.precision,
            "Recall": self.recall,
            "F1-Score": self.f1_score
        }
    
    def from_labels(
        self,
        target: ArrayLike,
        prediction: ArrayLike,
        labels: ArrayLike | None = None,
    ) -> ClassificationData:
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

        kind: ClassificationType = (
            "binary"
            if len(resolved_labels) == 2
            else "multiclass"
        )

        return ClassificationData(
            y_true=y_true,
            y_score=y_score,
            y_pred=y_pred,
            labels=resolved_labels,
            kind=kind 
        )

    def from_multiclass_probabilities(
        self,
        target: ArrayLike,
        probabilities: ArrayLike,
        *,
        labels: ArrayLike
    ) -> ClassificationData:
        y_true, y_score = self._validate_muticlass_input(target, probabilities)
        y_score = self._validate_probabilities(y_score)
        resolved_labels = self._validate_labels(labels)

        if len(resolved_labels) < 3:
            raise ValueError(
                "multiclass probabilities require at least three labels"
            )

        if y_score.shape[1] != len(resolved_labels):
            raise ValueError(
                "the number of probability columns must match labels"
            )

        self._validate_known_labels(y_true, resolved_labels, name="target")
        row_sums = np.sum(y_score, axis=1)

        if not np.allclose(row_sums, 1.0):
            raise ValueError(
                "each row of probabilities must sum to 1"
            )

        pred_indices = np.argmax(y_score, axis=1)
        y_pred = resolved_labels[pred_indices]

        return ClassificationData(
            y_true=y_true,
            y_score=y_score,
            y_pred=y_pred,
            labels=resolved_labels,
            kind="multiclass"
        )

    def from_binary_probabilities(
        self,
        target: ArrayLike,
        probabilities: ArrayLike,
        *,
        positive_label: Any ,
        negative_label: Any ,
        threshold: float = 0.5,
    )->ClassificationData:
        y_true, positive_score = self._validate_inputs(target, probabilities)

        y_score = self._validate_probabilities(positive_score)
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
            positive_score >= threshold,
            positive_label,
            negative_label,
        )

        y_score = np.column_stack((
            1.0 - positive_score,
            positive_score
        ))

        return ClassificationData(
            y_true=y_true,
            y_score=y_score,
            y_pred=y_pred,
            labels=resolved_labels,
            kind="binary"
        )

    def confusion_matrix_ndarray(self, data: ClassificationData) -> NDArray[np.int64]:
        labels = data.labels
        matrix = np.zeros((len(labels), len(labels)), dtype=np.int64)

        label_to_index = {
            label: index 
            for index, label in enumerate(labels)
        }

        for true_label, pred_label in zip(data.y_true, data.y_pred):
            row = label_to_index[true_label]
            colume = label_to_index[pred_label]
            matrix[row, colume] += 1

        return matrix

    def confusion_matrix(self, data: ClassificationData) -> Dict[str, str | Iterable]:    
        matrix = self.confusion_matrix_ndarray(data)
        return {
            "labels": data.labels.tolist(),
            "values": matrix.tolist()
        }

    def accuracy(self, data: ClassificationData) -> float:
        return float(np.mean(data.y_true == data.y_pred))
    
    def precision(self, data: ClassificationData) -> Dict[str, List[Any]]:
        matrix = self.confusion_matrix_ndarray(data)

        true_positive = np.diag(matrix)
        pred_positive = np.sum(matrix, axis=0)

        precision_scores = np.divide(
            true_positive,
            pred_positive,
            out=np.zeros_like(true_positive, dtype=np.float64),
            where = pred_positive != 0
        )

        return {
            "labels":data.labels.tolist(),
            "values": precision_scores.tolist()
        }

    def recall(self, data: ClassificationData) -> Dict[str, List[Any]]:
        matrix = self.confusion_matrix_ndarray(data)

        true_positive = np.diag(matrix)
        all_positive = np.sum(matrix, axis=1)

        recall_scores = np.divide(
            true_positive,
            all_positive,
            out=np.zeros_like(true_positive, dtype=np.float64),
            where = all_positive != 0
        )

        return {
            "labels":data.labels.tolist(),
            "values": recall_scores.tolist()
        }

    def f1_score(self, data: ClassificationData) -> Dict[str, List[Any]]:
        matrix = self.confusion_matrix_ndarray(data)

        true_positive = np.diag(matrix)
        false_positive = np.sum(matrix, axis=0) - true_positive
        false_negative = np.sum(matrix, axis=1) - true_positive

        denominator = (
            2 * true_positive
            + false_positive
            + false_negative
        )

        f1_score = np.divide(
            2 * true_positive,
            denominator,
            out = np.zeros_like(true_positive, dtype=np.float64),
            where = denominator !=0
        )

        return {
            "labels": data.labels.tolist(),
            "values": f1_score.tolist()
        }

    def roc(
        self, data: ClassificationData,
        *,
        thresholds: Iterable[float] | None = None,
        gap: float | None = None
    ):
        if data.y_score is None:
            raise ValueError("ROC requires probability scores")

        if data.kind == "binary":
            positive_labels = data.labels[1]
            scores = data.y_score[:, 1]
            binary_target = (data.y_true == positive_labels)
            reslut = self._roc_calculator(scores, binary_target, thresholds, gap)

            return {
                "labels": data.labels.tolist(),
                "values": reslut
            }

        else:
            reslut_roc = []
            for index, label in enumerate(data.labels):
                scores = data.y_score[:, index]
                binary_target = (data.y_true == label)
                reslut = self._roc_calculator(scores, binary_target, thresholds, gap)
                reslut_roc.append({label: reslut})

            return {
                "labels": data.labels.tolist(),
                "values": reslut_roc
            }

    def _roc_calculator(
            self,
            score: ArrayLike,
            actual_positive: ArrayLike,
            thresholds: Iterable[float] | None = None,
            gap: float | None = None
        ) -> Dict[str, List | float]:
            scores = np.asarray(score, dtype=np.float64)
            actual_positive = np.asarray(actual_positive, dtype=bool)

            if thresholds is not None:
                roc_thresholds = np.asarray(list(thresholds), dtype=np.float64)
            elif gap is not None:
                if not 0 < gap <= 1:
                    raise ValueError("gap must be between 0 and 1")

                roc_thresholds = np.arange(1.0, -gap, -gap)
                roc_thresholds = np.clip(roc_thresholds, 0.0, 1.0)
            else:
                roc_thresholds = np.r_[
                    np.inf,
                    np.sort(np.unique(scores))[::-1],
                ]

            false_positive_rates = []
            true_positive_rates = []

            for threshold in roc_thresholds:
                predicted_positive = (scores >= threshold)
                actual_negative = ~actual_positive
                predicted_negative = ~predicted_positive

                tp = np.sum(actual_positive & predicted_positive)
                fn = np.sum(actual_positive & predicted_negative)
                fp = np.sum(actual_negative & predicted_positive)
                tn = np.sum(actual_negative & predicted_negative)

                tpr = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

                true_positive_rates.append(float(tpr))
                false_positive_rates.append(float(fpr))

            return {
                "thresholds": roc_thresholds.tolist(),
                "tpr": true_positive_rates,
                "fpr": false_positive_rates,
            }

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

    def _validate_muticlass_input(
        self,
        target: ArrayLike,
        probabilities: ArrayLike,
    ) -> tuple[NDArray[Any], NDArray[Any]]:
        
        y_true = np.asarray(target)
        y_score = np.asarray(probabilities)

        if y_true.ndim != 1:
            raise ValueError("target must be one-dimensional")
        
        if y_score.ndim != 2:
            raise ValueError(
                "multiclass probabilities must be two-dimensional"
            )

        if y_true.size == 0 :
            raise ValueError(
                "multiclass probabilities must be two-dimensional"
            )

        if y_score.shape[0] == 0 or y_score.shape[1] == 0:
            raise ValueError(
                "target and probabilities must not be empty"
            )

        if y_true.shape[0] != y_score.shape[0]:
            raise ValueError(
                "target and probabilities must have the same number of samples"
            )

        return y_true, y_score
        
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

    


    
