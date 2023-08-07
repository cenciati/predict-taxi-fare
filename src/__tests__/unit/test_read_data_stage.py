# pylint: disable=redefined-outer-name
import os
from typing import List

import pandas as pd
import pytest

from src.pipeline.stages import read_data

DATA_PATH: str = os.path.join('./data/raw/test/workflow_test_data.parquet')


@pytest.fixture()
def read_data_result() -> pd.DataFrame:
    return read_data.fn(DATA_PATH)


def test_if_read_data_is_a_pandas_dataframe(read_data_result) -> None:
    assert isinstance(read_data_result, pd.DataFrame)


def test_if_read_data_has_crucial_columns(read_data_result) -> None:
    crucial_columns: List[str] = [
        'id',
        'fare_amount',
        'trip_distance',
        'extra',
        'tip_amount',
    ]
    assert all(
        column in read_data_result.columns for column in crucial_columns
    )
