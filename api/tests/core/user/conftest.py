from datetime import datetime

import pytest


@pytest.fixture
def user_create():
    return {
        "username": "tester",
        "first_name": "joe",
        "last_name": "test",
        "email": "tester@example.com",
        "password": "pass",
        "password_match": "pass",
    }


@pytest.fixture
def user_update_dict():
    return {
        "first_name": "joe_update",
        "last_name": "test_update",
        "email": "tester_update@example.com",
        "password": "pass_update",
        "password_match": "pass_update",
    }


@pytest.fixture
def user_update_private_dict():
    return {
        "verified_email": "tester@example.com",
        "roles": ["admin"],
        "disabled": True,
        "verified": True,
        "date_modified": datetime(2022, 3, 3, 0, 0),
        "last_login": datetime(2022, 4, 4, 0, 0),
    }


@pytest.fixture
def updated_user_dict():
    return {
        "type": "USER",
        "username": "tester",
        "first_name": "joe_update",
        "last_name": "test_update",
        "email": "tester_update@example.com",
        "verified_email": None,
        "roles": [],
        "disabled": False,
        "verified": False,
        "date_created": datetime(2020, 1, 1, 0, 0),
        "date_modified": datetime(2022, 2, 2, 0, 0),
        "last_login": None,
        "password_hash": "hashed_update",
    }


@pytest.fixture
def updated_user_private_dict():
    return {
        "type": "USER",
        "username": "tester",
        "first_name": "joe",
        "last_name": "test",
        "email": "tester@example.com",
        "verified_email": "tester@example.com",
        "roles": ["admin"],
        "disabled": True,
        "verified": True,
        "date_created": datetime(2020, 1, 1, 0, 0),
        "date_modified": datetime(2022, 3, 3, 0, 0),
        "last_login": datetime(2022, 4, 4, 0, 0),
        "password_hash": "hashed",
    }
