from unittest.mock import AsyncMock, patch

from fastapi import FastAPI

from app import main as uut


def test_app_setup():
    """Verify FastAPI instance returned."""

    actual = uut.app_setup()

    assert isinstance(actual, FastAPI)


@patch("app.main.init_db", AsyncMock(return_value=True))
async def test_app_init():
    """Verify initialization is successful."""

    actual = await uut.app_init()

    assert actual is True
