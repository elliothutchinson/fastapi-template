import pytest
from pydantic import SecretStr

from app.core.user import model as uut
from tests.factories.user_factory import (
    UserCreateFactory,
    UserPrivateFactory,
    UserPublicFactory,
    UserUpdateFactory,
    UserUpdatePrivateFactory,
)


def test_USER_ROLE():
    expected = "USER"

    actual = uut.USER_ROLE

    assert actual == expected


def test_USER_CACHE_PREFIX():
    expected = "USER"

    actual = uut.USER_CACHE_PREFIX

    assert actual == expected


def test_min_length_password_valid():
    password = SecretStr("password")

    expected = password

    actual = uut.min_length_password(None, password)

    assert actual == expected


def test_min_length_password_invalid():
    password = SecretStr("pas")

    with pytest.raises(ValueError, match="password needs to be at least 4 characters"):
        uut.min_length_password(None, password)


def test_matching_password_valid():
    password = SecretStr("password")
    values = {"password_match": SecretStr("password")}

    actual = uut.matching_password(None, password, values)

    assert actual == password


def test_matching_password_invalid_missing_password_match():
    password = SecretStr("password")
    values = {}

    with pytest.raises(ValueError, match="passwords don't match"):
        uut.matching_password(None, password, values)


def test_matching_password_invalid_password_match_none():
    password = SecretStr("password")
    values = {"password_match": None}

    with pytest.raises(ValueError, match="passwords don't match"):
        uut.matching_password(None, password, values)


def test_matching_password_invalid_different_password_match():
    password = SecretStr("password")
    values = {"password_match": SecretStr("different_password")}

    with pytest.raises(ValueError, match="passwords don't match"):
        uut.matching_password(None, password, values)


def test_UserPublic():
    user_public = UserPublicFactory.build()

    expected = user_public

    actual = uut.UserPublic(**user_public.dict())

    assert actual == expected


def test_UserPublic_defaults():
    user_public = UserPublicFactory.build(verified=True)

    expected = uut.UserPublic(**user_public.dict())
    expected.verified_email = None
    expected.date_modified = None
    expected.last_login = None

    actual = uut.UserPublic(
        **user_public.dict(exclude={"verified_email", "date_modified", "last_login"})
    )

    assert actual == expected


def test_UserPrivate():
    user_private = UserPrivateFactory.build()

    expected = user_private

    actual = uut.UserPrivate(**user_private.dict())

    assert actual == expected


def test_UserPrivate_defaults():
    user_private = UserPrivateFactory.build(verified=True)

    expected = uut.UserPrivate(**user_private.dict())
    expected.verified_email = None
    expected.date_modified = None
    expected.last_login = None

    actual = uut.UserPrivate(
        **user_private.dict(exclude={"verified_email", "date_modified", "last_login"})
    )

    assert actual == expected


def test_UserCreate():
    user_create = UserCreateFactory.build()

    expected = user_create

    actual = uut.UserCreate(**user_create.dict())

    assert actual == expected


def test_UserUpdate():
    user_update = UserUpdateFactory.build()

    expected = user_update

    actual = uut.UserUpdate(**user_update.dict())

    assert actual == expected


def test_UserUpdate_defaults():
    user_update = UserUpdateFactory.build()

    expected = uut.UserUpdate(**user_update.dict())
    expected.first_name = None
    expected.last_name = None
    expected.email = None
    expected.password_match = None
    expected.password = None

    actual = uut.UserUpdate()

    assert actual == expected


def test_UserUpdatePrivate():
    user_update_private = UserUpdatePrivateFactory.build()

    expected = user_update_private

    actual = uut.UserUpdatePrivate(**user_update_private.dict())

    assert actual == expected


def test_UserUpdatePrivate_defaults():
    user_update_private = UserUpdatePrivateFactory.build()

    expected = uut.UserUpdatePrivate(**user_update_private.dict())
    expected.verified_email = None
    expected.roles = None
    expected.disabled = None
    expected.last_login = None

    actual = uut.UserUpdatePrivate()

    assert actual == expected
