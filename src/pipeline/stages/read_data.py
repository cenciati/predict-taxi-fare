import pandas as pd

from prefect import get_run_logger, task
from src.pipeline.exceptions import NYCWorkflowException


@task(retries=2, retry_delay_seconds=20)
def read_data(data_path: str) -> pd.DataFrame:
    """It only accepts csv and parquet files."""
    logger = get_run_logger()
    if data_path.split(".")[-1] == "csv":
        raw_data: pd.DataFrame = pd.read_csv(data_path)
    elif data_path.split(".")[-1] == "parquet":
        raw_data: pd.DataFrame = pd.read_parquet(data_path)
    else:
        message: str = "Data format not accepted."
        logger.error("NYC workflow: %s", message)
        raise NYCWorkflowException(message)
    if len(raw_data) == 0:
        message: str = "Empty dataset."
        logger.error("NYC workflow: %s", message)
        raise NYCWorkflowException(message)
    logger.info("NYC workflow: data successfully read.")
    return insert_id_column_if_there_is_not(raw_data)


def insert_id_column_if_there_is_not(raw_data: pd.DataFrame) -> pd.DataFrame:
    if "id" not in raw_data.columns:
        raw_data["id"] = raw_data.index + 1
        return raw_data
    return raw_data
