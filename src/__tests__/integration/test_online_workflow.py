import os

import pandas as pd
import pytest

from src.pipeline.online_workflow import OnlineInferencePipeline

DATA_PATH: str = os.path.join('./data/raw/test/workflow_test_data.parquet')


@pytest.fixture
def online_pipeline():
    data = pd.read_parquet(DATA_PATH).to_dict('records')[0]
    return OnlineInferencePipeline(data)
