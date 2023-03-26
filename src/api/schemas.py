# pylint: disable=no-name-in-module, protected-access, no-self-argument, line-too-long
from datetime import datetime
from functools import wraps
from typing import Dict

from fastapi import Request
from pydantic import BaseModel, Field, ValidationError, validator


class InputMakeNewPrediction(BaseModel, frozen=True):
    """Expected data input format."""

    id: str
    lpep_pickup_datetime: datetime
    lpep_dropoff_datetime: datetime
    fare_amount: int | float
    trip_distance: int | float
    tip_amount: int | float
    extra: int | float
    payment_type: str = Field(..., max_length=3)
    vendor_id: str = Field(..., max_length=3)
    store_and_fwd_flag: str = Field(..., max_length=3)
    ratecode_id: str
    pu_location_id: str
    do_location_id: str
    passenger_count: int
    mta_tax: float
    tolls_amount: float
    improvement_surcharge: float
    trip_type: str = Field(..., max_length=3)
    congestion_surcharge: float

    @validator("vendor_id", always=True, allow_reuse=True)
    def ensure_vendor_id_consistency(cls, value: str) -> str:
        if value not in ["1", "2"]:
            raise ValidationError("Vendor ID must be 1 or 2.")  # type: ignore
        return value

    @validator("ratecode_id", always=True, allow_reuse=True)
    def ensure_ratecode_id_consistency(cls, value: str) -> str:
        if value not in ["1", "2", "3", "4", "5", "6"]:
            raise ValidationError("Rate code ID must be between 1 and 6.")  # type: ignore
        return value

    @validator("store_and_fwd_flag", always=True, allow_reuse=True)
    def ensure_store_and_fwd_flag_consistency(cls, value: str) -> str:
        if value.upper() not in ["Y", "N"]:
            raise ValidationError("Store and FWD flag must be 'Y' or 'N'.")  # type: ignore
        return value

    @validator("payment_type", always=True, allow_reuse=True)
    def ensure_payment_type_consistency(cls, value: str) -> str:
        if value not in ["1", "2", "3", "4", "5", "6"]:
            raise ValidationError("Payment type must be between 1 and 6.")  # type: ignore
        return value

    @validator("trip_type", always=True, allow_reuse=True)
    def ensure_trip_type_consistency(cls, value: str) -> str:
        if value not in ["1", "2"]:
            raise ValidationError("Trip type must be 1 or 2.")  # type: ignore
        return value


def construct_response(function):
    """Construct useful metadata in a JSON response for an endpoint."""

    @wraps(function)
    def wrap(request: Request, *args, **kwargs) -> Dict[str, str]:
        results = function(request, *args, **kwargs)
        response = {
            "message": results["message"],
            "method": request.method,
            "status-code": results["status-code"],
            "timestamp": datetime.now().isoformat(),
            "url": request.url._url,
        }
        if "data" in results:
            response["data"] = results["data"]
        return response

    return wrap
