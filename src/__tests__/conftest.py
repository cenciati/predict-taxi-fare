from typing import Generator

import pytest
from prefect.logging import disable_run_logger
from prefect.testing.utilities import prefect_test_harness


@pytest.fixture(autouse=True, scope='session')
def prefect_disable_logging() -> Generator:
    with disable_run_logger():
        yield


@pytest.fixture(autouse=True, scope='session')
def prefect_test_fixture() -> Generator:
    with prefect_test_harness():
        yield
