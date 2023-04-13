import os

import pytest

from app.core import config as uut
from tests.factories.config_factory import ConfigFactory
from tests.unit.util import convert_to_env_vars


@pytest.fixture
def _config_api_docs_enabled():
    # pylint: disable=duplicate-code
    config = ConfigFactory.build(api_docs_enabled=True)
    new_env = convert_to_env_vars(config.dict())
    original_env = dict(os.environ)
    os.environ.update(new_env)

    yield new_env

    os.environ.clear()
    os.environ.update(original_env)


def test_Config():
    config = ConfigFactory.build()
    actual = uut.Config(**config.dict())

    assert actual.dict() == config.dict()


def test_get_config():
    config = ConfigFactory.build()
    actual = uut.get_config()

    assert actual.dict() == config.dict()


def test_app_settings_api_docs_enabled(_config_api_docs_enabled):
    expected = {
        "title": "FastAPI-Template",
    }

    actual = uut.app_settings()

    assert actual == expected


def test_app_settings_api_docs_disabled():
    expected = {
        "title": "FastAPI-Template",
        "docs_url": None,
        "redoc_url": None,
    }

    actual = uut.app_settings()

    assert actual == expected
