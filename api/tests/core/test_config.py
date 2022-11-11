import pytest
from pydantic import SecretStr

from app.core import config as uut
from tests.util import create_config_dict


@pytest.fixture
def config_dict():

    return create_config_dict(override={"jwt_secret_key": SecretStr("changethis")})


def test_Config(config_dict):
    actual = uut.Config(**config_dict)

    assert actual.dict() == config_dict


def test_get_config(config_dict):
    actual = uut.get_config()

    assert actual.dict() == config_dict


def test_app_settings_api_docs_enabled(_config_api_docs_enabled):
    expected = {
        "title": "FastAPI-POC",
    }

    actual = uut.app_settings()

    assert actual == expected


def test_app_settings_api_docs_disabled():
    expected = {
        "title": "FastAPI-POC",
        "docs_url": None,
        "redoc_url": None,
    }

    actual = uut.app_settings()

    assert actual == expected
