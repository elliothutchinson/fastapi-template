from datetime import datetime

import pytest
from pydantic import SecretStr

from app.core.user import model as uut
from tests.util import password_hash_str


def test_USER_ROLE():
    actual = uut.USER_ROLE

    assert actual == "USER"


def test_USER_CACHE_PREFIX():
    actual = uut.USER_CACHE_PREFIX

    assert actual == "USER"


def test_min_length_password_valid():
    password = SecretStr("password")

    actual = uut.min_length_password(None, password)

    assert actual == password


def test_min_length_password_invalid():
    password = SecretStr("pas")

    with pytest.raises(ValueError, match=f"password needs to be at least 4 characters"):
        uut.min_length_password(None, password)


def test_matching_password_valid():
    password = SecretStr("password")
    values = {"password_match": SecretStr("password")}

    actual = uut.matching_password(None, password, values)

    assert actual == password


def test_matching_password_invalid_missing_password_match():
    password = SecretStr("password")
    values = {}

    with pytest.raises(ValueError, match=f"passwords don't match"):
        uut.matching_password(None, password, values)


def test_matching_password_invalid_password_match_none():
    password = SecretStr("password")
    values = {"password_match": None}

    with pytest.raises(ValueError, match=f"passwords don't match"):
        uut.matching_password(None, password, values)


def test_matching_password_invalid_different_password_match():
    password = SecretStr("password")
    values = {"password_match": SecretStr("different_password")}

    with pytest.raises(ValueError, match=f"passwords don't match"):
        uut.matching_password(None, password, values)


def test_User_optional_fields():
    user_dict = {
        "username": "tester",
        "first_name": "Joe",
        "last_name": "Tester",
        "email": "tester@example.com",
        "roles": ["USER"],
        "disabled": False,
        "date_created": datetime(2020, 1, 1, 0, 0),
    }

    expected = user_dict.copy()
    expected["verified_email"] = None
    expected["date_modified"] = None
    expected["last_login"] = None

    actual = uut.User(**user_dict)

    assert actual.dict() == expected


def test_User():
    user_dict = {
        "username": "tester",
        "first_name": "Joe",
        "last_name": "Tester",
        "email": "tester@example.com",
        "verified_email": "tester@example.com",
        "roles": ["USER"],
        "disabled": False,
        "date_created": datetime(2020, 1, 1, 0, 0),
        "date_modified": datetime(2020, 1, 2, 0, 0),
        "last_login": datetime(2020, 1, 3, 0, 0),
    }

    actual = uut.User(**user_dict)

    assert actual.dict() == user_dict


def test_UserCreate():
    user_create_dict = {
        "username": "tester",
        "first_name": "Joe",
        "last_name": "Tester",
        "email": "tester@example.com",
        "password": "password",
        "password_match": "password",
    }

    expected = user_create_dict.copy()
    expected["password"] = SecretStr("password")
    expected["password_match"] = SecretStr("password")

    actual = uut.UserCreate(**user_create_dict)

    assert actual.dict() == expected


def test_UserCreate_invalid_username():
    user_create_dict = {
        "username": "tes",
        "first_name": "Joe",
        "last_name": "Tester",
        "email": "tester@example.com",
        "password": "password",
        "password_match": "password",
    }

    with pytest.raises(ValueError, match="ensure this value has at least 4 characters"):
        uut.UserCreate(**user_create_dict)


def test_UserCreate_invalid_password_length():
    user_create_dict = {
        "username": "tester",
        "first_name": "Joe",
        "last_name": "Tester",
        "email": "tester@example.com",
        "password": "pas",
        "password_match": "pas",
    }

    with pytest.raises(ValueError, match="password needs to be at least 4 characters"):
        uut.UserCreate(**user_create_dict)


def test_UserCreate_invalid_password_match():
    user_create_dict = {
        "username": "tester",
        "first_name": "Joe",
        "last_name": "Tester",
        "email": "tester@example.com",
        "password": "password",
        "password_match": "password_match",
    }

    with pytest.raises(ValueError, match="passwords don't match"):
        uut.UserCreate(**user_create_dict)


def test_UserUpdate_optional_fields():
    user_update_dict = {}

    expected = {
        "first_name": None,
        "last_name": None,
        "email": None,
        "password": None,
        "password_match": None,
    }

    actual = uut.UserUpdate(**user_update_dict)

    assert actual.dict() == expected


def test_UserUpdate():
    user_update_dict = {
        "first_name": "Joe",
        "last_name": "Tester",
        "email": "tester@example.com",
        "password": "password",
        "password_match": "password",
    }

    expected = user_update_dict.copy()
    expected["password"] = SecretStr("password")
    expected["password_match"] = SecretStr("password")

    actual = uut.UserUpdate(**user_update_dict)

    assert actual.dict() == expected


def test_UserUpdate_invalid_password_length():
    user_update_dict = {
        "first_name": "Joe",
        "last_name": "Tester",
        "email": "tester@example.com",
        "password": "pas",
        "password_match": "pas",
    }

    with pytest.raises(ValueError, match="password needs to be at least 4 characters"):
        uut.UserUpdate(**user_update_dict)


def test_UserUpdate_invalid_password_match():
    user_update_dict = {
        "first_name": "Joe",
        "last_name": "Tester",
        "email": "tester@example.com",
        "password": "password",
        "password_match": "password_match",
    }

    with pytest.raises(ValueError, match="passwords don't match"):
        uut.UserUpdate(**user_update_dict)


def test_UserDb_optional_fields():
    user_db_dict = {
        "username": "tester",
        "first_name": "Joe",
        "last_name": "Tester",
        "email": "tester@example.com",
        "date_created": datetime(2020, 1, 1, 0, 0),
        "password_hash": password_hash_str(),
    }

    expected = user_db_dict.copy()
    expected["id"] = None
    expected["verified_email"] = None
    expected["roles"] = []
    expected["disabled"] = False
    expected["date_modified"] = None
    expected["last_login"] = None

    actual = uut.UserDb(**user_db_dict)

    assert actual.dict() == expected


def test_UserDb():
    user_db_dict = {
        "id": None,
        "username": "tester",
        "first_name": "Joe",
        "last_name": "Tester",
        "email": "tester@example.com",
        "verified_email": "tester@example.com",
        "roles": ["USER"],
        "disabled": False,
        "date_created": datetime(2020, 1, 1, 0, 0),
        "date_modified": datetime(2020, 1, 2, 0, 0),
        "last_login": datetime(2020, 1, 3, 0, 0),
        "password_hash": password_hash_str(),
    }

    actual = uut.UserDb(**user_db_dict)

    assert actual.dict() == user_db_dict
