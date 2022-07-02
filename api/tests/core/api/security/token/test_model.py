import pytest

from app.core.api.security.token import model as uut


@pytest.fixture
def access_token():
    return {"token_type": "Bearer", "access_token": "token"}


def test_AccessToken(access_token):
    # actual = uut.AccessToken(**access_token)
    # assert actual.dict() == access_token
    pass


def test_TokenDb(token_db_dict):
    actual = uut.TokenDb(**token_db_dict)
    assert actual.dict() == token_db_dict


def test_TokenUpdateDb(token_update_db_dict):
    actual = uut.TokenUpdateDb(**token_update_db_dict)
    assert actual.dict() == token_update_db_dict


def test_TokenData(token_data_dict):
    actual = uut.TokenData(**token_data_dict)
    assert actual.dict() == token_data_dict


def test_InvalidTokenException():
    with pytest.raises(uut.InvalidTokenException, match="test exception"):
        raise uut.InvalidTokenException("test exception")
