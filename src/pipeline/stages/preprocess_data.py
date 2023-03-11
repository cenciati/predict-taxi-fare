import os
from typing import List

import joblib
import pandas as pd
from prefect import get_run_logger, task

from src.pipeline.exceptions.nyc_workflow_exception import NYCWorkflowException

PREPROCESSORS_DIR: str = os.path.join("src", "pipeline", "preprocessors")


@task(retries=2, retry_delay_seconds=20)
def preprocess_data(cleaned_data_with_features: pd.DataFrame) -> pd.DataFrame:
    logger = get_run_logger()
    try:
        # Apply robust scaler
        for column in ["tip_amount", "extra"]:
            rs_preprocessor = joblib.load(
                os.path.join(PREPROCESSORS_DIR, "robust_scaler", f"{column}.joblib")
            )
            cleaned_data_with_features.loc[:, [column]] = rs_preprocessor.transform(
                cleaned_data_with_features.loc[:, [column]]
            )
        # Apply standard scaler
        for column in [
            "fare_amount",
            "tax_per_meter",
            "trip_distance",
            "trip_duration",
        ]:
            ss_preprocessor = joblib.load(
                os.path.join(PREPROCESSORS_DIR, "standard_scaler", f"{column}.joblib")
            )
            cleaned_data_with_features.loc[:, [column]] = ss_preprocessor.transform(
                cleaned_data_with_features.loc[:, [column]]
            )
        # Apply one-hot encoding
        cleaned_data_with_features = pd.get_dummies(
            cleaned_data_with_features, columns=["payment_type"], drop_first=True
        )
        selected_columns: List[str] = [
            "id",
            "fare_amount",
            "trip_distance",
            "tax_per_meter",
            "trip_duration",
            "tip_amount",
            "extra",
            "payment_type_2.0",
        ]
    except Exception as exc:
        raise NYCWorkflowException from exc
    logger.info("NYC workflow: data preprocessed.")
    return cleaned_data_with_features.loc[:, selected_columns]
