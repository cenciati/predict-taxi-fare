# pylint: disable=invalid-name, broad-exception-raised
import os
from typing import List

import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from src.database.green_taxi_schema import GreenTaxiSchema
from src.logging import logger


def ingest_data_into_database(
    connection_string: str, data_directory: str, files: List[str]
) -> None:
    """Function responsible for ingesting data into a database given a
    connection string.
    Args:
        connection_string (str): Information about the data source.
        data_directory (str): Directory path to the folder `data/`.
        files (list[str]): List of files to be read and imported into the database.
            This list must only contain one type of data format.
    """
    raw_data_reader = RawDataReader(data_directory=data_directory, files_name=files)
    raw_data: pd.DataFrame = raw_data_reader.read_data()
    logger.info("Ingesting %i records into the database...", len(raw_data))
    engine: Engine = GreenTaxiSchema().create_table(connection_string)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        raw_data.to_sql(
            name="green_taxi",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=100_000,
        )
    except Exception as exc:
        logger.error("Failed while importing data to the database %s", exc)
        raise Exception from exc
    finally:
        session.rollback()
    logger.info("Data ingestion completed.")


class RawDataReader:
    """Responsible for reading raw `parquet` or `csv` files as pandas dataframe."""

    def __init__(self, data_directory: str, files_name: List[str]) -> None:
        self.data_directory = data_directory
        self.files_name = files_name

    def read_data(self) -> pd.DataFrame:
        self._validate()
        logger.debug("Data is being read by %s.", self.__class__.__name__)
        if self.files_name[0].endswith(".parquet"):
            return self._read_as_parquet()
        return self._read_as_csv()

    def _validate(self) -> None:
        """Checks if there is at least one file to be read."""
        if len(self.files_name) == 0:
            logger.error("No file specified.")
            raise ValueError
        logger.debug("Data has been validated.")

    def _read_as_parquet(self) -> pd.DataFrame:
        """Read given parquet"""
        return pd.concat(
            pd.read_parquet(
                os.path.join(self.data_directory, "raw", "train", file_name)
            )
            for file_name in self.files_name
        )

    def _read_as_csv(self) -> pd.DataFrame:
        """Read given csv"""
        return pd.concat(
            pd.read_csv(os.path.join(self.data_directory, "raw", "train", file_name))
            for file_name in self.files_name
        )
