from datetime import datetime, timezone

import pytest

from app.core.api.security.token.model import TokenData


def token_id():
    return "633c20a9-6795-48a0-a759-f9c04c69fda9"


def date_created():
    return datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)


def date_expires():
    return datetime(2120, 1, 2, 0, 0, tzinfo=timezone.utc)


def token_db_data():
    return {
        "type": "token",
        "token_id": token_id(),
        "token_type": "login_token",
        "username": "tester",
        "date_created": date_created(),
        "date_expires": date_expires(),
        "date_redacted": None,
    }


@pytest.fixture
def token_db_dict():
    return token_db_data()


@pytest.fixture
def token_data_dict(token_db_dict, user):
    return {
        "metadata": token_db_dict,
        "data": user,
        "sub": "tester",
        "claim": "login_token",
        "exp": date_expires(),
    }


@pytest.fixture
def login_token():
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJtZXRhZGF0YSI6eyJ0eXBlIjoidG9rZW4iLCJ0b2tlbl9pZCI6IjYzM2MyMGE5LTY3OTUtNDhhMC1hNzU5LWY5YzA0YzY5ZmRhOSIsInRva2VuX3R5cGUiOiJsb2dpbl90b2tlbiIsInVzZXJuYW1lIjoidGVzdGVyIiwiZGF0ZV9jcmVhdGVkIjoiMjAyMC0wMS0wMSAwMDowMDowMCswMDowMCIsImRhdGVfZXhwaXJlcyI6IjIxMjAtMDEtMDIgMDA6MDA6MDArMDA6MDAiLCJkYXRlX3JlZGFjdGVkIjpudWxsfSwiZGF0YSI6eyJ1c2VybmFtZSI6InRlc3RlciIsImZpcnN0X25hbWUiOiJqb2UiLCJsYXN0X25hbWUiOiJ0ZXN0IiwiZW1haWwiOiJ0ZXN0ZXJAZXhhbXBsZS5jb20iLCJ2ZXJpZmllZF9lbWFpbCI6InRlc3RlckBleGFtcGxlLmNvbSIsInJvbGVzIjpbInVzZXIiXSwiZGlzYWJsZWQiOmZhbHNlLCJ2ZXJpZmllZCI6dHJ1ZSwiZGF0ZV9jcmVhdGVkIjoiMjAyMC0wMS0wMSAwMDowMDowMCIsImRhdGVfbW9kaWZpZWQiOiIyMDIwLTAxLTAxIDAwOjAwOjAwIiwibGFzdF9sb2dpbiI6IjIwMjAtMDEtMDEgMDA6MDA6MDAifSwic3ViIjoidGVzdGVyIiwiY2xhaW0iOiJsb2dpbl90b2tlbiIsImV4cCI6NDczMzU5NjgwMH0.flo5kMEtHkNk-Rucfeh8BcUKizX8ILo0lzCpnKZZKAw"


@pytest.fixture
def token_data(token_data_dict):
    return TokenData(**token_data_dict)
