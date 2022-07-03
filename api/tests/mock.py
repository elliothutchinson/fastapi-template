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


def create_db_config_dict():
    return {
        "db_host": "db",
        "db_port": 5432,
        "db_root_user": "root",
        "db_root_password": "password",
        "db_root_database": "template1",
        "db_app_user": "app",
        "db_app_password": "password",
        "db_app_database": "api",
        "db_table": "docs",
        "db_test_table": "test_docs",
    }


def create_core_config(override={}):
    cc = {
        "username_min_length": 1,
        "password_min_length": 4,
        "project_name": "API Template",
        "templates_dir": "/app/ui/templates",
        "login_token_expire_min": 1440.0,
        "verify_token_expire_min": 20160,
        "refresh_token_expire_min": 20160,
        "secret_key": "changethis",
        "token_path": "/token",
        "refresh_path": "/refresh",
        "login_path": "/login",
        "forgot_password_path": "/forgot_password",
        "forgot_username_path": "/forgot_username",
        "reset_path": "/reset",
        "user_path": "/user",
        "verify_path": "/verify",
        "base_url": "http://localhost",
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
