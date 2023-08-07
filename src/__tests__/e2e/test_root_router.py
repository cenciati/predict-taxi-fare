from http import HTTPStatus

from fastapi import status
from fastapi.testclient import TestClient

from src.api.server import app

client = TestClient(app)
BASE_URL: str = 'http://localhost:8000/api/v1/'


def test_root_should_endpoint_return_status_code_equal_200():
    response = client.get(BASE_URL)
    assert response.status_code == status.HTTP_200_OK


def test_root_endpoint_should_return_data_properly():
    response = client.get(BASE_URL)
    assert response.json()['message'] == HTTPStatus.OK.phrase
    assert response.json()['data'] == {'Go to': '/predict'}
    assert response.json()['url'] == BASE_URL
    assert response.json()['method'] == 'GET'
