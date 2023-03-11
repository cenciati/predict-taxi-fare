# pylint: disable=redefined-outer-name
import os
from typing import List

import pandas as pd
import pytest

from src.pipeline.stages import clean_data, create_features, read_data

DATA_PATH: str = os.path.join("./data/raw/test/workflow_test_data.parquet")


@pytest.fixture()
def create_features_result() -> pd.DataFrame:
    raw_data: pd.DataFrame = read_data.fn(DATA_PATH)
    cleaned_data: pd.DataFrame = clean_data.fn(raw_data)
    return create_features.fn(cleaned_data)


def test_if_new_features_were_created(create_features_result) -> None:
    new_features: List[str] = ["tax_per_meter", "trip_duration"]
    assert all(column in create_features_result.columns for column in new_features)
