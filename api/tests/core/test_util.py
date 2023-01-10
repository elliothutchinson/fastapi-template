import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from pydantic import BaseModel, SecretStr

from app.core import util as uut
from tests.util import convert_to_env_vars


class SomeClass(BaseModel):
    optional_attr_1: str = None
    optional_attr_2: str = None
    bool_attr: bool
    int_attr: int
    float_attr: float
    str_attr: str
    secret_attr: SecretStr


@pytest.fixture
def some_class_dict():

    return {
        "optional_attr_1": "optional",
        "bool_attr": "true",
        "int_attr": "42",
        "float_attr": "3.14",
        "str_attr": "string",
        "secret_attr": "secret",
    }


@pytest.fixture
def _some_class_env(some_class_dict):
    # pylint: disable=duplicate-code
    new_env = convert_to_env_vars(some_class_dict)
    original_env = dict(os.environ)
    os.environ.update(new_env)

    yield new_env

    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def datetime_dict():

    return {
        "key_1": datetime(2020, 1, 1, 0, 0),
        "key_2": datetime(2020, 1, 2, 0, 0),
        "more_keys": {
            "key_3": datetime(2020, 1, 3, 0, 0),
            "key_4": datetime(2020, 1, 4, 0, 0),
            "key_5": 42,
        },
    }


def test_PydanticModel():
    actual = uut.PydanticModel

    assert actual.__name__ == "PydanticModel"
    assert actual.__bound__ == BaseModel


def test_utc_now():
    before = datetime.utcnow()
    actual = uut.utc_now()
    after = datetime.utcnow()

    assert actual >= before
    assert actual <= after


@patch(
    "app.core.util.datetime",
    Mock(utcnow=Mock(return_value=datetime(2020, 1, 1, 1, 0, tzinfo=timezone.utc))),
)
def test_convert_timestamp_to_ttl_future_timestamp():
    timestamp = datetime(2020, 1, 1, 1, 1, tzinfo=timezone.utc).timestamp()
    actual = uut.convert_timestamp_to_ttl(timestamp)

    assert actual == 60


@patch(
    "app.core.util.datetime",
    Mock(utcnow=Mock(return_value=datetime(2020, 1, 1, 1, 0, tzinfo=timezone.utc))),
)
def test_convert_timestamp_to_ttl_expired_timestamp():
    timestamp = datetime(2020, 1, 1, 0, 1, tzinfo=timezone.utc).timestamp()
    actual = uut.convert_timestamp_to_ttl(timestamp)

    assert actual == 1


def test_convert_datetime_to_str(datetime_dict):
    expected = {
        "key_1": "2020-01-01 00:00:00",
        "key_2": datetime(2020, 1, 2, 0, 0),
        "more_keys": {
            "key_3": datetime(2020, 1, 3, 0, 0),
            "key_4": "2020-01-04 00:00:00",
            "key_5": 42,
        },
    }

    actual = datetime_dict
    uut.convert_datetime_to_str(actual, skip=["key_2", "key_3"])

    assert actual == expected


def test_convert_datetime_to_str_no_skip(datetime_dict):
    expected = {
        "key_1": "2020-01-01 00:00:00",
        "key_2": "2020-01-02 00:00:00",
        "more_keys": {
            "key_3": "2020-01-03 00:00:00",
            "key_4": "2020-01-04 00:00:00",
            "key_5": 42,
        },
    }

    actual = datetime_dict
    uut.convert_datetime_to_str(actual)

    assert actual == expected


def test_populate_from_env(_some_class_env, some_class_dict):
    expected = SomeClass(**some_class_dict).dict(exclude_defaults=True)
    expected["secret_attr"] = some_class_dict["secret_attr"]

    actual = uut.populate_from_env(SomeClass)

    assert actual == expected
