from typing import Any, Annotated, TypeAlias, Literal, Iterable, TypeVar, Generic
from collections.abc import Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod

from annotated_doc import Doc
import numpy as np
from numpy.typing import NDArray

EvaluationDataT = TypeVar("EvaluationDataT")

class BaseEvaluator(ABC, Generic[EvaluationDataT]):
    task_type: str

    def __init__(self) -> None:
        self.metrics: dict[str, Callable[..., Any]] = {}

    def _select_metrics(self, metrics)->dict[str, Callable[..., Any]]:
        if metrics is None:
            return self.metrics

        unknown_metrics = set(metrics) - self.metrics.keys()

        if unknown_metrics:
            raise ValueError(
                f"Unsupported metrics: {sorted(unknown_metrics)}"
            )

        return {
            name: self.metrics[name]
            for name in metrics
        }

    def evaluate(
        self,
        data: EvaluationDataT,
        *,
        metrics: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        selected_metrics = self._select_metrics(metrics)

        return {
            name: metric(data)
            for name, metric in selected_metrics.items()
        }

