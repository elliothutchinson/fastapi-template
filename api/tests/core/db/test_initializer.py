from unittest.mock import AsyncMock, patch

import pytest
from asyncpg import InvalidCatalogNameError

from app.core.db import initializer as uut
from app.core.db.service import get_db_context


@patch("app.core.db.service.asyncpg", AsyncMock())
def test_init_db():
    actual = uut.init_db()
    assert actual is True


@patch("app.core.db.service.asyncpg", AsyncMock())
async def test_config_db(db_config):
    actual = await uut.config_db(db_config=db_config)
    assert actual is True


async def test_create_user_if_not_exists_create(db_context):
    actual = await uut.create_user_if_not_exists(db_context=db_context)
    assert actual is True


@pytest.mark.expected_data(True)
async def test_create_user_if_not_exists_no_create(db_context):
    actual = await uut.create_user_if_not_exists(db_context=db_context)
    assert actual is False


@pytest.mark.expected_data(True)
async def test_user_exists_true(db_context):
    actual = await uut.user_exists(db_context=db_context)
    assert actual is True


async def test_user_exists_false(db_context):
    actual = await uut.user_exists(db_context=db_context)
    assert actual is False


async def test_create_user(db_context):
    actual = await uut.create_user(db_context=db_context)
    assert actual is True


@patch(
    "app.core.db.service.asyncpg",
    AsyncMock(connect=AsyncMock(side_effect=[InvalidCatalogNameError(), AsyncMock()])),
)
async def test_create_db_if_not_exists_create():
    db_context = get_db_context()
    actual = await uut.create_db_if_not_exists(
        app_user_context=db_context, root_user_context=db_context
    )
    assert actual is True


async def test_create_db_if_not_exists_no_create(db_context):
    actual = await uut.create_db_if_not_exists(
        app_user_context=db_context, root_user_context=db_context
    )
    assert actual is False


async def test_db_exists_true(db_context):
    actual = await uut.db_exists(db_context=db_context)
    assert actual is True


@patch(
    "app.core.db.service.asyncpg",
    AsyncMock(connect=AsyncMock(side_effect=InvalidCatalogNameError())),
)
async def test_db_exists_false():
    db_context = get_db_context()
    actual = await uut.db_exists(db_context=db_context)
    assert actual is False


async def test_create_db(db_context):
    actual = await uut.create_db(db_context=db_context)
    assert actual is True


async def test_create_table_if_not_exists_create(db_context):
    actual = await uut.create_table_if_not_exists(
        db_context=db_context, table=db_context.config.db_table
    )
    assert actual is True


@pytest.mark.expected_data(True)
async def test_create_table_if_not_exists_no_create(db_context):
    actual = await uut.create_table_if_not_exists(
        db_context=db_context, table=db_context.config.db_table
    )
    assert actual is False


@pytest.mark.expected_data(True)
async def test_table_exists_true(db_context):
    actual = await uut.table_exists(
        db_context=db_context, table=db_context.config.db_table
    )
    assert actual is True


async def test_table_exists_false(db_context):
    actual = await uut.table_exists(
        db_context=db_context, table=db_context.config.db_table
    )
    assert actual is False


async def test_create_table(db_context):
    actual = await uut.create_table(
        db_context=db_context, table=db_context.config.db_table
    )
    assert actual is True
