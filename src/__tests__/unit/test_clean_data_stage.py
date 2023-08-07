# pylint: disable=redefined-outer-name
import os
from typing import List

import pandas as pd
import pytest

from src.pipeline.stages import clean_data, read_data

DATA_PATH: str = os.path.join('./data/raw/test/workflow_test_data.parquet')


@pytest.fixture()
def clean_data_result() -> pd.DataFrame:
    raw_data: pd.DataFrame = read_data.fn(DATA_PATH)
    return clean_data.fn(raw_data)


def test_if_there_are_no_duplicated_data(clean_data_result) -> None:
    assert clean_data_result.duplicated().sum() == 0


def test_if_there_are_no_null_data(clean_data_result) -> None:
    columns_that_cant_have_nas: List[str] = ['payment_type', 'trip_type']
    assert not any(
        clean_data_result.loc[:, columns_that_cant_have_nas].isna().sum()
    )
