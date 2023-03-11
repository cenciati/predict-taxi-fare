# pylint: disable=invalid-name
from argparse import ArgumentParser, Namespace
from os import getenv
import os
from typing import Optional, Sequence

import numpy as np
import pandas as pd
from prefect import flow
from prefect.deployments import Deployment

import mlflow
from src.logging import logger
from src.pipeline.exceptions import NYCWorkflowException
from src.pipeline.stages import (
    persist_results,
    clean_data,
    create_features,
    preprocess_data,
    read_data,
)


PREFECT_DIR: str = os.path.join("prefect")


@flow(
    name="predict-taxi-tip-total-amount",
    version=getenv("GIT_COMMIT_SHA"),
)
def predict_total_amount_nyc_taxis_flow(
    data_path: str, model_name: Optional[str] = "ridge-regressor"
) -> None:
    mlflow_setup()
    try:
        raw_data: pd.DataFrame = read_data(data_path)
        cleaned_data: pd.DataFrame = clean_data(raw_data)
        cleaned_data_with_features: pd.DataFrame = create_features(cleaned_data)
        preprocessed_data: pd.DataFrame = preprocess_data(cleaned_data_with_features)
        model = mlflow.sklearn.load_model(f"models:/{model_name}/Production")
        predictions: np.ndarray = model.predict(
            preprocessed_data.drop("id", axis=1).to_numpy()
        )
        preprocessed_data["predictions"] = predictions
        persist_results(preprocessed_data)
    except NYCWorkflowException as exc:
        logger.critical(
            "predict_total_amount_nyc_taxis_flow` could not be completed. %s", exc
        )
        raise NYCWorkflowException from exc


def mlflow_setup() -> None:
    """Sets up the required information to access the models."""
    MLFLOW_TRACKING_URI: str = "http://127.0.0.1:5000"
    EXPERIMENT_NAME: str = "Experiment_02"
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)


def get_args(argv: Optional[Sequence[str]] = None) -> Namespace:
    """Manages command-line arguments.
    Args:
        argv (sequence[str]): Sequence of strings corresponding to
            the user given data through command-line interface.
    Returns:
        Namespace object containing all arguments passed.
    """
    parser = ArgumentParser()
    parser.add_argument(
        "-d",
        "--datapath",
        help="Complete data path to desired raw data file.",
        type=str,
    )
    return parser.parse_args(argv)


args: Namespace = get_args()
deployment = Deployment.build_from_flow(
    flow=predict_total_amount_nyc_taxis_flow,
    name="nyc-taxis-production",
    version=getenv("GIT_COMMIT_SHA"),
    parameters={"data_path": args.datapath},
    infra_overrides={"env": {"PREFECT_LOGGING_LEVEL": "DEBUG"}},
    work_queue_name="production",
    output=os.path.join(PREFECT_DIR, "nyc-taxis-production-deployment.yaml"),
)

if __name__ == "__main__":
    deployment.apply()
    predict_total_amount_nyc_taxis_flow(args.datapath)
