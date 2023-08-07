from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any, Dict

from fastapi import status
from fastapi.testclient import TestClient

from src.api.server import app

client = TestClient(app)
BASE_URL: str = 'http://localhost:8000/api/v1/predict/'
MOCK_DATA: Dict[str, Any] = {
    'id': '123',
    'lpep_pickup_datetime': str(datetime.now()),
    'lpep_dropoff_datetime': str(datetime.now() + timedelta(minutes=13)),
    'fare_amount': 12,
    'trip_distance': 8,
    'tip_amount': 9,
    'extra': 0,
    'payment_type': '1',
    'vendor_id': '555',
    'store_and_fwd_flag': 'Y',
    'ratecode_id': '48',
    'pu_location_id': '100',
    'do_location_id': '89',
    'passenger_count': 3,
    'mta_tax': 1,
    'tolls_amount': 3,
    'improvement_surcharge': 3,
    'trip_type': 'Street-hail',
    'congestion_surcharge': 1,
}


def test_predict_endpoint_should_return_status_code_equal_200():
    response = client.post(BASE_URL, json=MOCK_DATA)
    assert response.status_code == status.HTTP_200_OK


def test_predict_endpoint_should_return_response_metadata_properly():
    response = client.post(BASE_URL, json=MOCK_DATA)
    assert response.json()['message'] == HTTPStatus.OK.phrase
    assert response.json()['url'] == BASE_URL
    assert response.json()['model-name'] == 'ridge-regressor'
    assert response.json()['model-version'] == '2'
    assert response.json()['method'] == 'POST'
