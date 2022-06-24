import contextlib
from unittest.mock import AsyncMock, Mock

import pytest

from app.core.db import service as uut
from app.core.db.model import DbConnect


def doc_dict():
    return {
        "name": "test",
    }


@pytest.fixture
def db_connect(db_config):
    db_connect_dict = {
        "host": db_config.db_host,
        "port": db_config.db_port,
        "user": db_config.db_app_user,
        "password": db_config.db_app_password,
        "database": db_config.db_app_database,
    }
    return DbConnect(**db_connect_dict)


def test_get_db_connect_app_user(db_connect, db_config):
    actual = uut.get_db_connect_app_user(db_config=db_config)
    assert actual == db_connect


def test_get_db_connect_root_user(db_connect, db_config):
    db_connect.user = db_config.db_root_user
    db_connect.password = db_config.db_root_password
    db_connect.database = db_config.db_root_database

    actual = uut.get_db_connect_root_user(db_config=db_config)

    assert actual == db_connect


def test_get_db_context(db_config):
    actual = uut.get_db_context()
    assert actual.config == db_config
    assert type(actual.connection()) is contextlib._AsyncGeneratorContextManager


def test_get_db_context_passed_db_connect(db_connect, mocker):
    db_connect.user = "tester"
    mock_connect = Mock()
    mocker.patch("app.core.db.service.connection_manager", mock_connect)

    uut.get_db_context(db_connect=db_connect)
    mock_connect.assert_called_with(db_connect=db_connect)


def test_get_db_context_default_db_connect(db_connect, mocker):
    mock_connect = Mock()
    mocker.patch("app.core.db.service.connection_manager", mock_connect)

    uut.get_db_context()
    mock_connect.assert_called_with(db_connect=db_connect)


def test_connection_manager(db_connect):
    actual = uut.connection_manager(db_connect=db_connect)
    assert type(actual()) is contextlib._AsyncGeneratorContextManager


async def test_connection_manager_connection(db_connect, mocker):
    mock_close = AsyncMock()
    mock_connect = AsyncMock(return_value=AsyncMock(close=mock_close))
    mock_asyncpg = AsyncMock(connect=mock_connect)
    mocker.patch("app.core.db.service.asyncpg", mock_asyncpg)

    async with uut.connection_manager(db_connect=db_connect)():
        mock_connect.assert_awaited()
    mock_close.assert_awaited()


@pytest.mark.expected_data(doc_dict())
async def test_execute(db_context):
    async with db_context.connection() as conn:
        actual = await uut.execute(conn, "", [])
        assert actual == doc_dict()
