from typing import List

import numpy as np
import pandas as pd
from inflection import underscore

from prefect import get_run_logger, task
from src.pipeline.exceptions.nyc_workflow_exception import NYCWorkflowException


@task(retries=2, retry_delay_seconds=20)
def clean_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    logger = get_run_logger()
    try:
        raw_data.columns = [underscore(column) for column in raw_data.columns]
        raw_data.drop_duplicates(inplace=True)
        raw_data.dropna(
            subset=['payment_type', 'trip_type'], axis=0, inplace=True
        )
        raw_data: pd.DataFrame = treat_outliers(raw_data)
    except Exception as exc:
        raise NYCWorkflowException from exc
    logger.info('NYC workflow: data cleaned.')
    return raw_data


def treat_outliers(raw_data: pd.DataFrame) -> pd.DataFrame:
    logger = get_run_logger()
    might_have_outlier_columns: List[str] = [
        'passenger_count',
        'trip_distance',
        'fare_amount',
        'extra',
        'mta_tax',
        'tip_amount',
        'tolls_amount',
        'improvement_surcharge',
        'congestion_surcharge',
    ]
    for column in might_have_outlier_columns:
        q75, q25 = np.percentile(raw_data.loc[:, column], 75), np.percentile(
            raw_data.loc[:, column], 25
        )
        iqr: float = q75 - q25
        cut_off: float = 3.0 * iqr
        lower, upper = q25 - cut_off, q75 + cut_off
        mask: List[bool] = [
            not (x < lower or x > upper) for x in raw_data.loc[:, column]
        ]
        raw_data: pd.DataFrame = raw_data.loc[mask, :]
    logger.info('NYC workflow: outliers treated.')
    return raw_data
