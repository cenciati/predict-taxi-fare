# pylint: disable=no-name-in-module
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.logging import logger
from src.pipeline.online_workflow import OnlineInferencePipeline

predictions_router = APIRouter()


class InputMakeNewPrediction(BaseModel):
    """Expected data input format."""

    id: str
    lpep_pickup_datetime: datetime
    lpep_dropoff_datetime: datetime
    fare_amount: int | float
    trip_distance: int | float
    tip_amount: int | float
    extra: int | float
    payment_type: str
    vendor_id: str | int
    store_and_fwd_flag: str
    ratecode_id: str
    pu_location_id: str
    do_location_id: str
    passenger_count: int
    mta_tax: float
    tolls_amount: float
    improvement_surcharge: float
    trip_type: str
    congestion_surcharge: float


@predictions_router.post(
    "/predict/",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, Dict[str, float]],
)
def predict_taxi_ride_total_amount(input_: InputMakeNewPrediction):
    data: dict = input_.dict()
    try:
        if len(data) == 0:
            logger.debug("User sent empty data.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can't make a prediction with no data.",
            )
        pipeline = OnlineInferencePipeline(data=data)
        prediction: Dict[str, float] = pipeline.execute()
        return {"data": prediction}
    except Exception as exc:
        logger.error("Error while trying to make the prediction. %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc
