from quickmlops.evaluation import BaseEvaluator

class ClusteringEvaluator(BaseEvaluator):
    task_type = "clustering"

    def __init__(self) -> None:
        super().__init__()
        self.metrics = {
            "Silhouette Coefficient": self.silhouette_coefficient,
            "DBI": self.dbi,
            "CHI": self.chi,
        }

    def silhouette_coefficient(self, X, labels, **kwargs):
        pass

    def dbi(self, X, labels, **kwargs):
        pass

    def chi(self, X, labels, **kwargs):
        pass
