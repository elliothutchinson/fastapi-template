from unittest.mock import AsyncMock, Mock, patch

from app.core.db import initialize as uut
from app.core.security.token import RevokedTokenDb
from app.core.user.model import UserDb


def test_doc_models():
    actual = uut.doc_models()

    assert actual == [UserDb, RevokedTokenDb]


@patch("app.core.db.initialize.init_beanie", AsyncMock())
async def test_init_db():
    mock_app = Mock()

    actual = await uut.init_db(mock_app)

    assert actual is True
