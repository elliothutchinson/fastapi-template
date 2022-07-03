from datetime import datetime

import pytest

from app.core.db.model import DbConfig, DbContext
from app.core.user.model import User
from tests.mock import (
    create_db_config_dict,
    mock_connection_factory,
    password_hash_of_plaintext_test,
)


@pytest.fixture
def db_config_dict():
    return create_db_config_dict()


@pytest.fixture
def db_config(db_config_dict):
    return DbConfig(**db_config_dict)


@pytest.fixture
def db_context(db_config, request):
    marker = request.node.get_closest_marker("expected_data")
    expected = None
    throw = None
    multi_expected = None
    if marker:
        print(f"args: {marker.args}")
        print(f"kwargs: {marker.kwargs}")
        if "multi_expected" in marker.kwargs:
            multi_expected = marker.kwargs["multi_expected"]
        if marker.args:
            expected = marker.args[0]
        if len(marker.args) > 1:
            throw = marker.args[1]
    db_context_dict = {
        "config": db_config,
        "connection": mock_connection_factory(
            expected=expected, throw=throw, multi_expected=multi_expected
        ),
    }
    return DbContext(**db_context_dict)


@pytest.fixture
def password_hash():
    return password_hash_of_plaintext_test()


@pytest.fixture
def user_dict():
    return {
        "username": "tester",
        "first_name": "joe",
        "last_name": "test",
        "email": "tester@example.com",
        "verified_email": "tester@example.com",
        "roles": ["user"],
        "disabled": False,
        "verified": True,
        "date_created": datetime(2020, 1, 1, 0, 0),
        "date_modified": datetime(2020, 1, 1, 0, 0),
        "last_login": datetime(2020, 1, 1, 0, 0),
    }


@pytest.fixture
def user(user_dict):
    return User(**user_dict)
