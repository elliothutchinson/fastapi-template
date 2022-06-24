import pytest
from pydantic import SecretStr

from app.core.api.security import crypt as uut


@pytest.fixture
def password():
    return SecretStr("test")


def test_context():
    actual = uut.context
    assert actual.schemes() == ("bcrypt",)


def test_verify_password_success(password, password_hash):
    actual = uut.verify_password(password=password, password_hash=password_hash)
    assert actual is True


def test_verify_password_fail(password_hash):
    actual = uut.verify_password(
        password=SecretStr("wrong"), password_hash=password_hash
    )
    assert actual is False


def test_hash_password(password):
    actual = uut.hash_password(password=password)
    assert uut.verify_password(password=password, password_hash=actual) is True
