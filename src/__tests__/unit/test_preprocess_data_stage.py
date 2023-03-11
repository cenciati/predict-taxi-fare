# pylint: disable=redefined-outer-name
import os
from typing import List

import pandas as pd
import pytest

from src.pipeline.stages import clean_data, create_features, preprocess_data, read_data

DATA_PATH: str = os.path.join("./data/raw/test/workflow_test_data.parquet")


@pytest.fixture()
@pytest.mark.unit
def preprocess_data_result() -> pd.DataFrame:
    raw_data: pd.DataFrame = read_data.fn(DATA_PATH)
    cleaned_data: pd.DataFrame = clean_data.fn(raw_data)
    cleaned_data_with_features: pd.DataFrame = create_features.fn(cleaned_data)
    return preprocess_data.fn(cleaned_data_with_features)


@pytest.fixture()
@pytest.mark.unit
def selected_columns() -> List[str]:
    return [
        "id",
        "fare_amount",
        "trip_distance",
        "trip_duration",
        "tip_amount",
        "extra",
        "tax_per_meter",
        "payment_type_2.0",
    ]


@pytest.mark.unit
def test_if_it_has_the_expected_number_of_columns(
    preprocess_data_result, selected_columns
) -> None:
    assert len(preprocess_data_result.columns) == len(selected_columns)


@pytest.mark.unit
def test_if_columns_were_selected_properly(
    preprocess_data_result, selected_columns
) -> None:
    assert sorted(list(preprocess_data_result.columns)) == sorted(selected_columns)


@pytest.mark.unit
def test_if_columns_are_between_the_range_zero_and_one(preprocess_data_result) -> None:
    assert preprocess_data_result.loc[:, "fare_amount"].median() <= 1.0
    assert preprocess_data_result.loc[:, "trip_distance"].median() <= 1.0
    assert preprocess_data_result.loc[:, "trip_duration"].median() <= 1.0
    assert preprocess_data_result.loc[:, "tip_amount"].median() <= 1.0
    assert preprocess_data_result.loc[:, "extra"].median() <= 1.0
    assert preprocess_data_result.loc[:, "tax_per_meter"].median() <= 1.0
