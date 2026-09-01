from typing import TypeAlias, Literal, Dict, Any
from quickmlops.model_evaluators.base_evaluator import BaseEvaluator

from quickmlops.model_evaluators.classification import ClassificationEvaluator, ClassificationData
from quickmlops.model_evaluators.clustering import ClusteringEvaluator, ClusteringData
from quickmlops.model_evaluators.regression import RegressionEvaluator, RegressionData


TaskType: TypeAlias = Literal[
    "classification",
    "regression",
    "clustering"
]

class EvaluationService:

    def evaluator_for(
        self,
        task_type: TaskType
    ) -> BaseEvaluator:
        match task_type:
            case "classification":
                return ClassificationEvaluator()
            case "regression":
                return RegressionEvaluator()
            case "clustering" :
                return ClusteringEvaluator()
            case _:
                raise ValueError("Cannot evaluate a model with an unknown task type.")

    def submit(
        self,
        evaluator: BaseEvaluator,
        data: ClusteringData | ClassificationData | RegressionData
    )-> Dict[str, Any]:
        return evaluator.evaluate(data)