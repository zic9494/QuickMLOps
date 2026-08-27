from dataclasses import dataclass
from numpy.typing import NDArray, ArrayLike
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
    adjusted_rand_score,
    adjusted_mutual_info_score,
    v_measure_score
)
from typing import Any
import numpy as np

from quickmlops.evaluation import BaseEvaluator

@dataclass(frozen=True)
class ClusteringData:
    X: NDArray[np.float64] | None
    predicted_labels: NDArray[Any]
    true_labels: NDArray[Any] | None

class ClusteringEvaluator(BaseEvaluator[ClusteringData]):
    task_type = "clustering"

    def __init__(self) -> None:
        super().__init__()
        self.metrics = {
            "silhouette": self.silhouette_coefficient,
            "davies_bouldin": self.davies_bouldin_index,
            "calinski_harabasz": self.calinski_harabasz_index,
            "adjusted_rand": self.ari,
            "adjusted_mutual_info": self.ami,
            "v_measure": self.v_measure,
        }

    def evaluate(self, data: ClusteringData, *, metrics = None):
        if metrics is None:
            select_metrics: list[str] = []

            if data.X is not None:
                select_metrics.extend([
                    "silhouette",
                    "davies_bouldin",
                    "calinski_harabasz",
                ])

            if data.true_labels is not None:
                select_metrics.extend([
                    "adjusted_rand",
                    "adjusted_mutual_info",
                    "v_measure",
                ])

            metrics = select_metrics

        return super().evaluate(data, metrics=metrics)

    def from_features(
       self,
       features: ArrayLike,
       predicted_labels: ArrayLike
    ) -> ClusteringData:
        X = self._validate_feature(features)
        y_pred = self._validate_predicted_labels(predicted_labels)

        self._validate_sample_sizes(
            features=X,
            predicted_labels=y_pred,
            true_labels=None
        )

        return ClusteringData(
            X=X,
            predicted_labels=y_pred,
            true_labels=None
        )

    def from_labels(
        self,
        true_labels: ArrayLike,
        predicted_labels: ArrayLike
    ) -> ClusteringData:
        y_pred = self._validate_predicted_labels(predicted_labels)
        y_true = self._validate_true_labels(true_labels)

        self._validate_sample_sizes(
            features=None,
            predicted_labels=y_pred,
            true_labels=y_true
        )

        return ClusteringData(
            X=None,
            predicted_labels=y_pred,
            true_labels=y_true,
        )

    def from_features_and_labels(
        self,
        features: ArrayLike,
        true_labels: ArrayLike,
        predicted_labels: ArrayLike
    ) -> ClusteringData:
        X = self._validate_feature(features)
        y_pred = self._validate_predicted_labels(predicted_labels)
        y_true = self._validate_true_labels(true_labels)

        self._validate_sample_sizes(
            features=X,
            predicted_labels=y_pred,
            true_labels=y_true
        )

        return ClusteringData(
            X=X,
            predicted_labels=y_pred,
            true_labels=y_true
        )

    def silhouette_coefficient(self, data: ClusteringData) -> float:
        self._validate_internal_metric_data(data)
        assert data.X is not None

        return float(
            silhouette_score(
                data.X,
                data.predicted_labels
            )
        )

    def davies_bouldin_index(self, data: ClusteringData) -> float:
        self._validate_internal_metric_data(data)
        assert data.X is not None

        unique_labels = np.unique(data.predicted_labels)
        if unique_labels.size < 2:
            raise ValueError(
                "davies-bouldin index requires at least two clusters"
            )

        return float(
            davies_bouldin_score(data.X, data.predicted_labels)
        )

    def calinski_harabasz_index(self, data: ClusteringData) -> float:
        self._validate_internal_metric_data(data)
        assert data.X is not None

        return float(
            calinski_harabasz_score(data.X, data.predicted_labels)
        )

    def ari(self, data: ClusteringData) -> float:
        self._validate_external_metric_data(data)
        assert data.true_labels is not None

        return float(
            adjusted_rand_score(data.true_labels, data.predicted_labels)
        )

    def ami(self, data: ClusteringData) -> float:
        self._validate_external_metric_data(data)
        assert data.true_labels is not None

        return float(
            adjusted_mutual_info_score(data.true_labels, data.predicted_labels)
        )

    def v_measure(self, data: ClusteringData) -> float:
        self._validate_external_metric_data(data)
        assert data.true_labels is not None

        return float(
            v_measure_score(data.true_labels, data.predicted_labels)
        )

    def _validate_predicted_labels(
        self,
        predicted_labels: ArrayLike
    ) -> NDArray[Any]:
        labels = np.asarray(predicted_labels)

        if labels.ndim != 1:
            raise ValueError("predicted_labels must be one-dimensional")

        if labels.size == 0:
            raise ValueError("predicted_labels must not be empty")

        return labels

    def _validate_true_labels(
        self,
        true_labels: ArrayLike
    ) -> NDArray[Any]:
        labels = np.asarray(true_labels)

        if labels.ndim != 1:
            raise ValueError("true_labels must be one-dimensional")

        if labels.size == 0:
            raise ValueError("true_labels must not be empty")

        return labels

    def _validate_feature(
        self,
        features: ArrayLike
    ) -> NDArray[np.float64]:
        try:
            resolved_features = np.asarray(features, dtype=np.float64)
        except (TypeError, ValueError) as exc:
            raise ValueError("features must contain numeric values") from exc

        if resolved_features.ndim != 2:
            raise ValueError("features must be two-dimensional")

        if resolved_features.shape[0] == 0 or resolved_features.shape[1] == 0:
            raise ValueError("features must not be empty")

        if not np.all(np.isfinite(resolved_features)):
            raise ValueError("features must contain only finite values")

        return resolved_features

    def _validate_sample_sizes(
        self,
        *,
        features: NDArray[np.float64] | None = None,
        predicted_labels: NDArray[Any],
        true_labels: NDArray[Any] | None = None,
    ) -> None:
        expected_size = predicted_labels.shape[0]

        if features is not None and features.shape[0] != expected_size:
            raise ValueError(
                "features and predicted_labels must contain the same "
                f"number of samples; got {features.shape[0]} and {expected_size}"
            )

        if true_labels is not None and true_labels.shape[0] != expected_size:
            raise ValueError(
                "true_labels and predicted_labels must contain the same "
                f"number of samples; got {true_labels.shape[0]} and {expected_size}"
            )

    def _validate_internal_metric_data(
        self,
        data: ClusteringData
    ) -> None:
        if data.X is None:
            raise ValueError(
                "internal clustering metrics require feature data"
            )

    def _validate_external_metric_data(
            self,
            data: ClusteringData
        ) -> None:

            if data.true_labels is None:
                raise ValueError(
                    "external clustering metrics require true labels"
                )
