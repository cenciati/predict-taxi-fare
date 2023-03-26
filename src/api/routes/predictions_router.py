# pylint: disable=unused-argument, invalid-name
from http import HTTPStatus
from typing import Dict

from fastapi import APIRouter, HTTPException, Request, status

from src.api.schemas import InputMakeNewPrediction, construct_response
from src.logging import logger
from src.pipeline.online_workflow import OnlineInferencePipeline

predictions_router = APIRouter()
PREDICTION_JSON_RESPONSE_FORMAT = Dict[str, str | Dict[str, float]]
model_name: str = "ridge-regressor"
model_version: str = "2"


@predictions_router.post(
    "/predict/",
    status_code=status.HTTP_200_OK,
    response_model=PREDICTION_JSON_RESPONSE_FORMAT,
)
@construct_response
def _predict(request: Request, input_: InputMakeNewPrediction):
    try:
        print(input_)
        pipeline = OnlineInferencePipeline(data=input_.dict(), model_name=model_name)
        prediction: Dict[str, float] = pipeline.execute()
        return {
            "message": HTTPStatus.OK.phrase,
            "status-code": status.HTTP_200_OK,
            "model-name": model_name,
            "model-version": model_version,
            "data": prediction,
        }
    except Exception as exc:
        logger.error("Error while trying to make the prediction. %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc
