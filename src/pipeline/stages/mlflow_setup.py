# pylint: disable=invalid-name
import mlflow


def mlflow_setup() -> None:
    """Sets up the required information to access the models."""
    MLFLOW_TRACKING_URI: str = "http://127.0.0.1:5000"
    EXPERIMENT_NAME: str = "Experiment_02"
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
