import pytest
from pydantic import SecretStr, ValidationError

from app.core.db import model as uut


@pytest.fixture
def db_config():
    return {
        "db_host": "host",
        "db_port": 1234,
        "db_root_user": "rootuser",
        "db_root_password": SecretStr("pass"),
        "db_root_database": "template1",
        "db_app_user": "appuser",
        "db_app_password": SecretStr("pass"),
        "db_app_database": "app",
        "db_table": "docs",
        "db_test_table": "test_docs",
    }


@pytest.fixture
def db_connect():
    return {
        "host": "host",
        "port": 1234,
        "user": "rootuser",
        "password": SecretStr("pass"),
        "database": "app",
    }


@pytest.fixture
def db_context(db_config):
    return {
        "config": uut.DbConfig(**db_config),
        "connection": lambda x: x,
    }


def test_DbConfig_valid(db_config):
    actual = uut.DbConfig(**db_config).dict()
    assert actual == db_config


def test_DbConfig_missing_required(db_config):
    for key in db_config:
        missing = db_config.copy()
        missing.pop(key)

        with pytest.raises(
            ValidationError, match=f"1 validation error for DbConfig\n{key}"
        ):
            uut.DbConfig(**missing)


def test_DbConnect_valid(db_connect):
    actual = uut.DbConnect(**db_connect)
    assert actual.dict() == db_connect


def test_DbConnect_missing_required(db_connect):
    for key in db_connect:
        missing = db_connect.copy()
        missing.pop(key)

        with pytest.raises(
            ValidationError, match=f"1 validation error for DbConnect\n{key}"
        ):
            uut.DbConnect(**missing)


def test_DbContext_valid(db_context):
    actual = uut.DbContext(**db_context).dict()
    assert actual == db_context


def test_DbContext_missing_required(db_context):
    for key in db_context:
        missing = db_context.copy()
        missing.pop(key)

        with pytest.raises(
            ValidationError, match=f"1 validation error for DbContext\n{key}"
        ):
            uut.DbContext(**missing)


def test_ResourceAlreadyExistsException():
    with pytest.raises(uut.ResourceAlreadyExistsException, match="test exception"):
        raise uut.ResourceAlreadyExistsException("test exception")


def test_ResourceNotFoundException():
    with pytest.raises(uut.ResourceNotFoundException, match="test exception"):
        raise uut.ResourceNotFoundException("test exception")
