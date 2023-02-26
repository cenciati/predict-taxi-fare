# pylint: disable=no-name-in-module
from sqlalchemy import BigInteger, Column, DateTime, Float, String
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base

from src.logging import logger

Base = declarative_base()


class GreenTaxiSchema(Base):
    """SQLAlchemy green taxi table mapping."""

    __tablename__ = "green_taxi"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    VendorID = Column(String, nullable=False)
    lpep_pickup_datetime = Column(DateTime, nullable=False)
    lpep_dropoff_datetime = Column(DateTime, nullable=False)
    store_and_fwd_flag = Column(String, nullable=True)
    RatecodeID = Column(String, nullable=True)
    PULocationID = Column(String, nullable=False)
    DOLocationID = Column(String, nullable=False)
    passenger_count = Column(Float, nullable=True)
    trip_distance = Column(Float, nullable=False)
    fare_amount = Column(Float, nullable=False)
    extra = Column(Float, nullable=False)
    mta_tax = Column(Float, nullable=False)
    tip_amount = Column(Float, nullable=False)
    tolls_amount = Column(Float, nullable=False)
    ehail_fee = Column(Float, nullable=True)
    improvement_surcharge = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=True)
    payment_type = Column(String, nullable=True)
    trip_type = Column(String, nullable=True)
    congestion_surcharge = Column(Float, nullable=True)

    @classmethod
    def create_table(cls, connection_string: str) -> Engine:
        logger.debug(
            "Creating table %s using the following connection string %s.",
            cls.__tablename__,
            connection_string,
        )
        engine: Engine = create_engine(connection_string)
        Base.metadata.create_all(bind=engine, checkfirst=True)
        return engine

    def __repr__(self) -> str:
        return f"""
            <GreenTaxiSchema(VendorID={self.VendorID},
            lpep_pickup_datetime={self.lpep_pickup_datetime},
            lpep_dropoff_datetime={self.lpep_dropoff_datetime},
            store_and_fwd_flag={self.store_and_fwd_flag},
            RatecodeID={self.RatecodeID},
            PULocationID={self.PULocationID},
            DOLocationID={self.DOLocationID},
            passenger_count={self.passenger_count},
            trip_distance={self.trip_distance},
            fare_amount={self.fare_amount},
            extra={self.extra},
            mta_tax={self.mta_tax},
            tip_amount={self.tip_amount},
            tolls_amount={self.tolls_amount},
            ehail_fee={self.ehail_fee},
            improvement_surcharge={self.improvement_surcharge},
            total_amount={self.total_amount},
            payment_type={self.payment_type},
            trip_type={self.trip_type},
            congestion_surcharge={self.congestion_surcharge})>
            """
