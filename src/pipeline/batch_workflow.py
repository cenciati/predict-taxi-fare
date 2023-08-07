# pylint: disable=invalid-name, ungrouped-imports, inconsistent-return-statements, dangerous-default-value
import os
from argparse import ArgumentParser, Namespace
from os import getenv
from typing import Optional, Sequence

import numpy as np
import pandas as pd
from prefect.deployments import Deployment
from prefect.task_runners import SequentialTaskRunner

import mlflow
from prefect import flow
from src.__logs__.logging import logger
from src.pipeline.exceptions import NYCWorkflowException
from src.pipeline.stages import (
    clean_data,
    create_features,
    mlflow_setup,
    persist_results,
    preprocess_data,
    read_data,
)

PREFECT_DIR: str = os.path.join('prefect')


@flow(
    name='predict-taxi-tip-total-amount',
    version=getenv('GIT_COMMIT_SHA'),
    task_runner=SequentialTaskRunner(),
)
def predict_total_amount_nyc_taxis_flow(
    data_path: str,
    model_name: Optional[str] = 'ridge-regressor',
) -> None:
    logger.info('Setting up MLflow...')
    mlflow_setup()
    try:
        logger.info('Reading data in the data path %s...', data_path)
        raw_data: pd.DataFrame = read_data(data_path)
        logger.info('Preparing data...')
        cleaned_data: pd.DataFrame = clean_data(raw_data)
        cleaned_data_with_features: pd.DataFrame = create_features(
            cleaned_data
        )
        preprocessed_data: pd.DataFrame = preprocess_data(
            cleaned_data_with_features
        )
        model = mlflow.sklearn.load_model(f'models:/{model_name}/Production')
        logger.info('Making the predictions...')
        predictions: np.ndarray = model.predict(
            preprocessed_data.drop('id', axis=1).to_numpy()
        )
        preprocessed_data['predictions'] = predictions
        # Model may not be able to predict every row,
        # certainly some of them will be dropped through the flow.
        # In order to keep the resiliency in the index, I'm recreating it.
        preprocessed_data.reset_index(drop=True, inplace=True)
        logger.info('Persisting result data...')
        persist_results(preprocessed_data)
    except NYCWorkflowException as exc:
        logger.critical(
            '`predict_total_amount_nyc_taxis_flow` could not be completed. %s',
            exc,
        )
        raise NYCWorkflowException from exc


if __name__ == '__main__':

    def get_args(argv: Optional[Sequence[str]] = None) -> Namespace:
        """Manages command-line arguments.
        Args:
            argv (sequence[str]): Sequence of strings corresponding to
                the user given data through command-line interface.
        Returns:
            Namespace object containing all arguments passed.
        """
        parser = ArgumentParser()
        parser.add_argument(
            '-d',
            '--datapath',
            help='Complete data path to desired raw data file.',
            type=str,
        )
        return parser.parse_args(argv)

    args: Namespace = get_args()
    deployment = Deployment.build_from_flow(
        flow=predict_total_amount_nyc_taxis_flow,
        name='nyc-taxis-production',
        version=getenv('GIT_COMMIT_SHA'),
        parameters={'data_path': args.datapath},
        infra_overrides={'env': {'PREFECT_LOGGING_LEVEL': 'DEBUG'}},
        work_queue_name='production',
        output=os.path.join(
            PREFECT_DIR, 'nyc-taxis-production-deployment.yaml'
        ),
    )
    deployment.apply()
    # As this deployment isn't scheduled yet,
    # I'm running it manually
    predict_total_amount_nyc_taxis_flow(args.datapath)
