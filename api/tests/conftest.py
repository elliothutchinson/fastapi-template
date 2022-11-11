import os
from unittest.mock import AsyncMock, Mock

import pytest
from beanie import init_beanie
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient
from pydantic import SecretStr

from app.core.security.token import RevokedTokenDb
from app.core.user.model import User, UserCreate, UserDb, UserUpdate
from app.main import app
from tests.util import (
    access_token_id_str,
    access_token_refreshed_id_str,
    convert_to_env_vars,
    create_config_dict,
    refresh_token_id_str,
    user_db_dict,
)


@pytest.fixture
def _config_api_docs_enabled():
    config = create_config_dict({"api_docs_enabled": True})
    new_env = convert_to_env_vars(config)
    original_env = dict(os.environ)
    os.environ.update(new_env)

    yield new_env

    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def client():

    return TestClient(app)


@pytest.fixture
def user_db():

    return UserDb(**user_db_dict())


@pytest.fixture
def user():

    return User(**user_db_dict())


@pytest.fixture
def user_create():

    return UserCreate(
        **user_db_dict(),
        password=SecretStr("password"),
        password_match=SecretStr("password"),
    )


@pytest.fixture
def user_update():

    return UserUpdate(
        first_name="Joey",
        last_name="Testing",
        email="joe_tester@example.com",
        password="changed_password",
        password_match="changed_password",
    )


@pytest.fixture
async def _setup_db():
    client = AsyncMongoMockClient()
    await init_beanie(
        document_models=[UserDb, RevokedTokenDb],
        database=client.get_database(name="testdb"),
    )

    yield

    await client.drop_database("testdb")


@pytest.fixture
async def _setup_db_user_db(_setup_db, user_db):
    await user_db.save()


@pytest.fixture
def _setup_cache(mocker):
    mocker.patch(
        "app.core.db.cache.aioredis.from_url",
        Mock(
            return_value=AsyncMock(
                get=AsyncMock(return_value=None),
                set=AsyncMock(return_value=True),
                delete=AsyncMock(return_value=1),
            )
        ),
    )


@pytest.fixture
def _setup_cache_user_db(mocker, user_db):
    mocker.patch(
        "app.core.db.cache.aioredis.from_url",
        Mock(
            return_value=AsyncMock(
                get=AsyncMock(return_value=user_db.json()),
                set=AsyncMock(return_value=True),
                delete=AsyncMock(return_value=1),
            )
        ),
    )


@pytest.fixture
def access_token():

    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl9pZCI6ImVkMmI1ZjU1LTc5ZWMtNGNiMC1hZTViLWZiYjJhOWFkZDI4MyIsImNsYWltIjoiQUNDRVNTX1RPS0VOIiwiZXhwIjoxNTc3ODQwNDAwLCJzdWIiOiJ0ZXN0ZXIiLCJkYXRhIjp7InVzZXJuYW1lIjoidGVzdGVyIiwiZmlyc3RfbmFtZSI6IkpvZSIsImxhc3RfbmFtZSI6IlRlc3RlciIsImVtYWlsIjoidGVzdGVyQGV4YW1wbGUuY29tIiwidmVyaWZpZWRfZW1haWwiOiJ0ZXN0ZXJAZXhhbXBsZS5jb20iLCJyb2xlcyI6WyJVU0VSIl0sImRpc2FibGVkIjpmYWxzZSwiZGF0ZV9jcmVhdGVkIjoiMjAyMC0wMS0wMSAwMDowMDowMCIsImRhdGVfbW9kaWZpZWQiOiIyMDIwLTAxLTAyIDAwOjAwOjAwIiwibGFzdF9sb2dpbiI6IjIwMjAtMDEtMDMgMDA6MDA6MDAifX0.wvWESiDeC83XM-r6N6OayQS3gFqv2qZYMclSp8L7os8"


@pytest.fixture
def access_token_refreshed():

    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl9pZCI6ImZiMjhiNWM0LTUyYzAtNDlkOC05Y2ZhLWI4YjE1MDM5MTA1NyIsImNsYWltIjoiQUNDRVNTX1RPS0VOIiwiZXhwIjoxNTc3ODQyMjAwLCJzdWIiOiJ0ZXN0ZXIiLCJkYXRhIjp7InVzZXJuYW1lIjoidGVzdGVyIiwiZmlyc3RfbmFtZSI6IkpvZSIsImxhc3RfbmFtZSI6IlRlc3RlciIsImVtYWlsIjoidGVzdGVyQGV4YW1wbGUuY29tIiwidmVyaWZpZWRfZW1haWwiOiJ0ZXN0ZXJAZXhhbXBsZS5jb20iLCJyb2xlcyI6WyJVU0VSIl0sImRpc2FibGVkIjpmYWxzZSwiZGF0ZV9jcmVhdGVkIjoiMjAyMC0wMS0wMSAwMDowMDowMCIsImRhdGVfbW9kaWZpZWQiOiIyMDIwLTAxLTAyIDAwOjAwOjAwIiwibGFzdF9sb2dpbiI6IjIwMjAtMDEtMDMgMDA6MDA6MDAifX0.x5l2Qw4uTzaeCsNsPrPVyNeS54eBvNanbx7Xf6ih5rc"


@pytest.fixture
def refresh_token():

    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl9pZCI6IjczOTlhNGQ4LTBjMzMtNGY4OS05MjEyLTkxOTRmZDkxYjg4NiIsImNsYWltIjoiUkVGUkVTSF9UT0tFTiIsImV4cCI6MTU3Nzg0NzYwMCwic3ViIjoidGVzdGVyIiwiZGF0YSI6bnVsbH0.8Tt2Vzx_c3IFO8Bb5apkfTtP4dE8TnyCVXdwIwsR8Fc"


@pytest.fixture
def access_token_id():

    return access_token_id_str()


@pytest.fixture
def access_token_refreshed_id():

    return access_token_refreshed_id_str()


@pytest.fixture
def refresh_token_id():

    return refresh_token_id_str()


@pytest.fixture
def auth_headers(access_token):

    return {"Authorization": f"Bearer {access_token}"}
