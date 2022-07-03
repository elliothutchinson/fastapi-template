from datetime import datetime

import pytest
from pydantic import SecretStr, ValidationError

from app.core.user import model as uut


@pytest.fixture
def user_db():
    return {
        "type": "USER",
        "username": "tester",
        "first_name": "joe",
        "last_name": "test",
        "email": "tester@example.com",
        "verified_email": "tester@example.com",
        "roles": ["user"],
        "disabled": False,
        "verified": False,
        "date_created": datetime.now(),
        "date_modified": datetime.now(),
        "last_login": datetime.now(),
        "password_hash": "hashed",
    }


@pytest.fixture
def user_update_db():
    return {
        "first_name": "joe",
        "last_name": "test",
        "email": "tester@example.com",
        "verified_email": "tester@example.com",
        "roles": ["user"],
        "disabled": False,
        "verified": False,
        "date_modified": datetime.now(),
        "last_login": datetime.now(),
        "password_hash": "hashed",
    }


def test_USER_DOC_TYPE():
    assert uut.USER_DOC_TYPE == "USER"


def test_min_length_password_when_valid():
    password = SecretStr("pass")

    actual = uut.min_length_password(None, password)

    assert actual.get_secret_value() == password.get_secret_value()


def test_min_length_password_when_invalid():
    password = SecretStr("p")

    with pytest.raises(ValueError, match="password needs to be at least 4 characters"):
        uut.min_length_password(None, password)


def test_matching_password_valid():
    password = SecretStr("pass")
    values = {"password_match": SecretStr("pass")}

    actual = uut.matching_password(None, password, values)

    assert actual.get_secret_value() == password.get_secret_value()


def test_matching_password_missing():
    password = SecretStr("pass")
    values = {}

    with pytest.raises(ValueError, match="passwords don't match"):
        uut.matching_password(None, password, values)


def test_matching_password_invalid():
    password = SecretStr("pass")

    values = {"password_match": SecretStr("pas")}

    with pytest.raises(ValueError, match="passwords don't match"):
        uut.matching_password(None, password, values)


def test_User_valid(user_dict):
    actual = uut.User(**user_dict).dict()

    assert actual == user_dict


def test_User_default_fields(user_dict):
    default_fields = 3
    user_dict.pop("verified_email")
    user_dict.pop("date_modified")
    user_dict.pop("last_login")

    actual = uut.User(**user_dict).dict()

    assert len(actual) == len(user_dict) + default_fields

    assert actual["verified_email"] == None
    assert actual["date_modified"] == None
    assert actual["last_login"] == None


def test_User_email_invalid(user_dict):
    user_dict["email"] = "invalid"

    with pytest.raises(ValidationError, match="1 validation error for User\nemail"):
        uut.User(**user_dict)


def test_User_verified_email_invalid(user_dict):
    user_dict["verified_email"] = "invalid"

    with pytest.raises(
        ValidationError, match="1 validation error for User\nverified_email"
    ):
        uut.User(**user_dict)


def test_UserCreate_valid(user_create):
    actual = uut.UserCreate(**user_create).dict()

    for key in user_create:
        if key == "password" or key == "password_match":
            assert actual[key].get_secret_value() == user_create[key]
        else:
            assert actual[key] == user_create[key]

    assert len(actual) == len(user_create)


def test_UserCreate_username_invalid(user_create):
    user_create["username"] = ""

    with pytest.raises(
        ValidationError, match="1 validation error for UserCreate\nusername"
    ):
        uut.UserCreate(**user_create)


def test_UserCreate_email_invalid(user_create):
    user_create["email"] = "invalid"

    with pytest.raises(
        ValidationError, match="1 validation error for UserCreate\nemail"
    ):
        uut.UserCreate(**user_create)


def test_UserCreate_password_mismatch(user_create):
    user_create["password_match"] = "mismatch"

    with pytest.raises(
        ValidationError, match="1 validation error for UserCreate\npassword"
    ):
        uut.UserCreate(**user_create)


def test_UserCreate_password_invalid(user_create):
    user_create["password"] = "p"
    user_create["password_match"] = "p"

    with pytest.raises(
        ValidationError, match="1 validation error for UserCreate\npassword"
    ):
        uut.UserCreate(**user_create)


def test_UserCreate_missing_required(user_create):
    for key in user_create:
        missing = user_create.copy()
        missing.pop(key)

        error_message = f"1 validation error for UserCreate\n{key}"
        if key == "password_match":
            error_message = f"2 validation errors for UserCreate\n{key}"

        with pytest.raises(ValidationError, match=error_message):
            uut.UserCreate(**missing)


def test_UserUpdate_optional_fields(user_update_dict):
    user_update_dict.pop("password")
    user_update_dict.pop("password_match")

    for key in user_update_dict:
        just_one = {}
        just_one[key] = user_update_dict[key]

        actual = uut.UserUpdate(**just_one).dict()

        assert actual[key] == just_one[key]


def test_UserUpdate_email_invalid():
    user_update = {
        "email": "invalid",
    }

    with pytest.raises(
        ValidationError, match="1 validation error for UserUpdate\nemail"
    ):
        uut.UserUpdate(**user_update)


def test_UserUpdate_password_valid():
    user_update = {
        "password": "pass",
        "password_match": "pass",
    }

    actual = uut.UserUpdate(**user_update).dict()

    for key in user_update:
        assert actual[key].get_secret_value() == user_update[key]


def test_UserUpdate_password_mismatch():
    user_update = {
        "password": "pass",
        "password_match": "mismatch",
    }

    with pytest.raises(
        ValidationError, match="1 validation error for UserUpdate\npassword"
    ):
        uut.UserUpdate(**user_update)


def test_UserUpdate_password_invalid():
    user_update = {
        "password": "p",
        "password_match": "p",
    }

    with pytest.raises(
        ValidationError, match="1 validation error for UserUpdate\npassword"
    ):
        uut.UserUpdate(**user_update)


def test_UserUpdate_password_match_missing():
    user_update = {
        "password": "pass",
    }

    with pytest.raises(
        ValidationError, match="1 validation error for UserUpdate\npassword"
    ):
        uut.UserUpdate(**user_update)


def test_UserUpdatePrivate_optional_fields(user_update_private_dict):
    for key in user_update_private_dict:
        just_one = {}
        just_one[key] = user_update_private_dict[key]

        actual = uut.UserUpdatePrivate(**just_one).dict()

        assert actual[key] == just_one[key]


def test_UserUpdatePrivate_verified_email_invalid():
    user_update_private = {
        "verified_email": "invalid",
    }

    with pytest.raises(
        ValidationError,
        match="1 validation error for UserUpdatePrivate\nverified_email",
    ):
        uut.UserUpdatePrivate(**user_update_private)


def test_UserDb_valid(user_db):
    actual = uut.UserDb(**user_db).dict()

    assert actual == user_db


def test_UserDb_default_fields(user_db):
    remove = [
        "type",
        "verified_email",
        "roles",
        "disabled",
        "verified",
        "date_modified",
        "last_login",
    ]

    for field in remove:
        user_db.pop(field)

    default_fields = len(remove)

    actual = uut.UserDb(**user_db).dict()

    assert len(actual) == len(user_db) + default_fields

    assert actual["type"] == "USER"
    assert actual["verified_email"] == None
    assert actual["roles"] == []
    assert actual["disabled"] == False
    assert actual["verified"] == False
    assert actual["date_modified"] == None
    assert actual["last_login"] == None


def test_UserDb_username_invalid(user_db):
    user_db["username"] = ""

    with pytest.raises(
        ValidationError, match="1 validation error for UserDb\nusername"
    ):
        uut.UserDb(**user_db)


def test_UserDb_email_invalid(user_db):
    user_db["email"] = "invalid"

    with pytest.raises(ValidationError, match="1 validation error for UserDb\nemail"):
        uut.UserDb(**user_db)


def test_UserDb_verified_email_invalid(user_db):
    user_db["verified_email"] = "invalid"

    with pytest.raises(
        ValidationError, match="1 validation error for UserDb\nverified_email"
    ):
        uut.UserDb(**user_db)


def test_UserUpdateDb_optional_fields(user_update_db):
    for key in user_update_db:
        just_one = {}
        just_one[key] = user_update_db[key]

        actual = uut.UserUpdateDb(**user_update_db).dict()

        assert actual[key] == just_one[key]


def test_UserUpdateDb_email_invalid():
    user_update_db = {"email": "invalid"}

    with pytest.raises(
        ValidationError, match="1 validation error for UserUpdateDb\nemail"
    ):
        uut.UserUpdateDb(**user_update_db)


def test_UserUpdateDb_verified_email_invalid():
    user_update_db = {"verified_email": "invalid"}

    with pytest.raises(
        ValidationError, match="1 validation error for UserUpdateDb\nverified_email"
    ):
        uut.UserUpdateDb(**user_update_db)
