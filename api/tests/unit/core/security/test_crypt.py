import pytest
from pydantic import SecretStr

from app.core.security import crypt as uut
from tests import util


@pytest.fixture
def password():
    return SecretStr("password")


@pytest.fixture
def password_hash():
    return util.password_hash()


def test_context():
    actual = uut.context

    assert actual.schemes() == ("bcrypt",)


def test_verify_password(password, password_hash):
    actual = uut.verify_password(password=password, password_hash=password_hash)

    assert actual is True


def test_verify_password_failure(password_hash):
    actual = uut.verify_password(
        password=SecretStr("invalid"), password_hash=password_hash
    )

    assert actual is False


def test_hash_password(password):
    actual_hash = uut.hash_password(password=password)
    actual_result = uut.verify_password(password=password, password_hash=actual_hash)

    assert isinstance(actual_hash, str)
    assert actual_result is True
