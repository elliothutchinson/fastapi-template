from contextlib import asynccontextmanager
from datetime import datetime

import orjson

from app.core.model import CoreConfig

MIN_IN_YEAR = 525960.0


def doc_row(doc_dict):
    return {"doc": orjson.dumps(doc_dict)}


def doc_row_user(override={}):
    return doc_row(create_user_dict(override=override))


def doc_row_full_user(override={}):
    return doc_row(create_full_user_dict(override=override))


def password_hash_of_plaintext_test():
    return "$2b$12$/7OKph0Xyk.a86Vre53f3eKRKYlaNUuOPdrhuqSZrdMhEziMuNjdi"


def create_core_config(override={}):
    cc = {
        "username_min_length": 1,
        "password_min_length": 4,
        "project_name": "API Template",
        "login_token_expire_min": 1440.0,
        "secret_key": "changethis",
        "token_path": "/token",
        "login_path": "/login",
        "user_path": "/user",
        "current_api": "API_V1",
        "api_v1": "/api/v1",
    }
    for key in override:
        cc[key] = override[key]
    return CoreConfig(**cc)


def create_user_dict(override={}):
    ud = {
        "username": "tester",
        "first_name": "joe",
        "last_name": "test",
        "email": "tester@example.com",
        "date_created": datetime(2020, 1, 1, 0, 0),
        "password_hash": "hashed",
    }
    for key in override:
        ud[key] = override[key]
    return ud


def create_full_user_dict(override={}):
    ud = {
        "verified_email": "tester@example.com",
        "roles": ["user"],
        "disabled": False,
        "verified": True,
        "date_modified": datetime(2020, 1, 1, 0, 0),
        "last_login": datetime(2020, 1, 1, 0, 0),
        "password_hash": password_hash_of_plaintext_test(),
    }
    for key in override:
        ud[key] = override[key]
    return create_user_dict(ud)


def mock_connection_factory(expected=None, throw=None, multi_expected=None):
    @asynccontextmanager
    async def mock_connection():
        yield MockConnection(expected, throw=throw, multi_expected=multi_expected)

    return mock_connection


class MockConnection:
    def __init__(self, expected, throw=None, multi_expected=[]):
        self.expected = expected
        self.throw = throw
        self.multi_expected = multi_expected

    async def prepare(self, query):
        return self

    async def fetchrow(self, *params):
        if self.multi_expected:
            return self.multi_expected.pop(0)
        if self.throw:
            raise self.throw
        return self.expected

    async def fetch(self, *params):
        return await self.fetchrow(params)

    async def execute(self, *params):
        return self.expected
