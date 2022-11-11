import re
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import main as uut


@pytest.fixture
def client():
    app = uut.app_setup()

    return TestClient(app)


def test_app_setup():
    actual = uut.app_setup()

    assert type(actual) == FastAPI


@patch("app.main.init_db", AsyncMock(return_value=True))
async def test_app_init():
    actual = await uut.app_init()

    assert actual == True


def test_openapi_api_docs_enabled(_config_api_docs_enabled, client):
    actual = client.get("/docs")
    actual_title = re.search(
        r"<\W*title\W*(.*)</title>", actual.text, re.IGNORECASE
    ).group(1)

    assert actual.status_code == 200
    assert actual_title == "FastAPI-POC - Swagger UI"


def test_openapi_api_docs_disabled(client):
    actual = client.get("/docs")

    assert actual.status_code == 404


def test_redoc_api_docs_enabled(_config_api_docs_enabled, client):
    actual = client.get("/redoc")
    actual_title = re.search(
        r"<\W*title\W*(.*)</title>", actual.text, re.IGNORECASE
    ).group(1)

    assert actual.status_code == 200
    assert actual_title == "FastAPI-POC - ReDoc"


def test_redoc_api_docs_disabled(client):
    actual = client.get("/redoc")

    assert actual.status_code == 404
