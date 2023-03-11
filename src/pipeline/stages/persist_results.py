import os
import pandas as pd
from prefect import get_run_logger, task

from src.pipeline.exceptions.nyc_workflow_exception import NYCWorkflowException


REPORTS_DIR: str = os.path.join("reports")


@task(retries=2, retry_delay_seconds=20)
def persist_results(preprocessed_data: pd.DataFrame) -> None:
    logger = get_run_logger()
    try:
        preprocessed_data.to_parquet(
            os.path.join(REPORTS_DIR, "outputs", "workflow_results.parquet")
        )
    except Exception as exc:
        raise NYCWorkflowException from exc
    logger.info("NYC workflow: results saved.")
