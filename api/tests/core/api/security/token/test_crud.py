import pytest

from app.core.api.security.token import crud as uut
from tests.core.api.conftest import token_db_data
from tests.mock import doc_row


def test_get_token_doc_id():
    actual = uut.get_token_doc_id(token_id="test")
    assert actual == "TOKEN::test"


async def test_create_token(db_context, token_db):
    actual = await uut.create_token(db_context=db_context, token_db=token_db)
    assert actual == token_db


async def test_update_token(db_context, token_db, token_update_db):
    expected = token_db.dict()
    expected["date_redacted"] = token_update_db.date_redacted
    actual = await uut.update_token(
        db_context=db_context, token_db=token_db, token_update_db=token_update_db
    )
    assert actual.dict() == expected


@pytest.mark.expected_data([doc_row(token_db_data())])
async def test_get_valid_tokens_for_user(db_context, token_db):
    actual = await uut.get_valid_tokens_for_user(
        db_context=db_context, username="tester"
    )
    assert actual == [token_db]
