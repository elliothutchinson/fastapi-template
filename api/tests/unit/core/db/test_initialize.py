from unittest.mock import AsyncMock, Mock, patch

from app.core.db import initialize as uut
from app.core.todo.repo import TodoDb, TodoListDb
from app.core.user.repo import UserDb


def test_doc_models():
    expected = [UserDb, TodoListDb, TodoDb]

    actual = uut.doc_models()

    assert actual == expected


@patch("app.core.db.initialize.init_beanie", AsyncMock())
async def test_init_db():
    mock_app = Mock()

    actual = await uut.init_db(mock_app)

    assert actual is True
