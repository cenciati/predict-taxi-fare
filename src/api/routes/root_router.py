from http import HTTPStatus

# pylint: disable=unused-argument
from typing import Dict

from fastapi import APIRouter, Request, status

from src.api.schemas import construct_response

root_router = APIRouter()


@root_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=Dict[str, str | Dict[str, str]],
)
@construct_response
def _root(request: Request):
    """Health check."""
    return {
        "message": HTTPStatus.OK.phrase,
        "status-code": status.HTTP_200_OK,
        "data": {"Go to": "/predict"},
    }
