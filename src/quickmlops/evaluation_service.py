from typing import TypeAlias, Literal, Dict, Any
from quickmlops.model_evaluators.base_evaluator import BaseEvaluator

from quickmlops.model_evaluators.classification import ClassificationEvaluator, ClassificationData
from quickmlops.model_evaluators.clustering import ClusteringEvaluator, ClusteringData
from quickmlops.model_evaluators.regression import RegressionEvaluator, RegressionData
from quickmlops.types_defs import TaskType

EvaluationData: TypeAlias = (
    ClassificationData
    | RegressionData
    | ClusteringData
)

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
        data: EvaluationData
    )-> Dict[str, Any]:
        return evaluator.evaluate(data)