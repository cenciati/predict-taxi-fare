import pandas as pd

from prefect import get_run_logger, task
from src.pipeline.exceptions.nyc_workflow_exception import NYCWorkflowException


@task(retries=2, retry_delay_seconds=20)
def create_features(cleaned_data: pd.DataFrame) -> pd.DataFrame:
    logger = get_run_logger()
    try:
        cleaned_data["tax_per_meter"] = (
            cleaned_data.loc[:, "trip_distance"] * cleaned_data.loc[:, "mta_tax"]
        )
        cleaned_data["trip_duration"] = (
            cleaned_data.loc[:, "lpep_dropoff_datetime"]
            - cleaned_data.loc[:, "lpep_pickup_datetime"]
        )
        cleaned_data["trip_duration"] = cleaned_data["trip_duration"].dt.seconds / 60
    except Exception as exc:
        raise NYCWorkflowException from exc
    logger.info("NYC workflow: features created.")
    return cleaned_data
