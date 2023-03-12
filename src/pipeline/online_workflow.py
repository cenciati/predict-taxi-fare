from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from prefect.logging import disable_run_logger

import mlflow
from src.logging import logger
from src.pipeline.exceptions import NYCWorkflowException
from src.pipeline.stages import (
    clean_data,
    create_features,
    mlflow_setup,
    preprocess_data,
)


class OnlineInferencePipeline:
    """Data workflow for online inference."""

    def __init__(
        self, data: Dict[str, Any], model_name: Optional[str] = "ridge-regressor"
    ) -> None:
        self.data = data
        self.model_name = model_name

    def execute(self) -> Dict[str, float]:
        """Triggers the workflow for predicting a taxi ride total tip amount."""
        try:
            logger.info("Preparing data...")
            preprocessed_data: pd.DataFrame = self.__prepare_data(
                pd.DataFrame(self.data, index=[0])
            )
            logger.info("Making predictions...")
            result_data: pd.DataFrame = self.__make_prediction(preprocessed_data)
            logger.info("Returning result data...")
            return result_data.loc[0, ["id", "predictions"]].to_dict()
        except NYCWorkflowException as exc:
            logger.critical(
                "`OnlineInferencePipeline` workflow could not be completed. %s", exc
            )
            raise NYCWorkflowException from exc

    def __prepare_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        with disable_run_logger():
            cleaned_data: pd.DataFrame = clean_data.fn(raw_data)
            cleaned_data_with_features: pd.DataFrame = create_features.fn(cleaned_data)
            return preprocess_data.fn(cleaned_data_with_features)

    def __make_prediction(self, preprocessed_data: pd.DataFrame) -> pd.DataFrame:
        logger.info("Setting up MLflow...")
        mlflow_setup()
        model = mlflow.sklearn.load_model(f"models:/{self.model_name}/Production")
        predictions: np.ndarray = model.predict(
            preprocessed_data.drop("id", axis=1).to_numpy()
        )
        preprocessed_data["predictions"] = predictions
        return preprocessed_data
