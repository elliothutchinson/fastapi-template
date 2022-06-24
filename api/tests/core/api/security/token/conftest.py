from datetime import datetime

import pytest

from app.core.api.security.token.model import TokenDb, TokenUpdateDb


@pytest.fixture
def token_db(token_db_dict):
    return TokenDb(**token_db_dict)


@pytest.fixture
def token_update_db_dict():
    return {
        "date_redacted": datetime(2020, 1, 1, 0, 0),
    }


@pytest.fixture
def token_update_db(token_update_db_dict):
    return TokenUpdateDb(**token_update_db_dict)
