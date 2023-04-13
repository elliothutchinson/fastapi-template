from unittest.mock import AsyncMock, Mock

import pytest
from beanie import init_beanie
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient

from app.core.db.initialize import doc_models
from app.core.security.auth import get_user_from_token
from app.main import app
from tests import util
from tests.factories.token_factory import AuthTokenFactory
from tests.factories.user_factory import UserPublicFactory


@pytest.fixture
def auth_headers():
    auth_token = AuthTokenFactory.build(jan_01_2020=True)

    return util.authorization_header(auth_token.access_token)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def override_get_user_from_token(client):
    user_public = UserPublicFactory.build()

    def _override_get_user_from_token():
        return user_public

    client.app.dependency_overrides[get_user_from_token] = _override_get_user_from_token

    yield user_public

    client.app.dependency_overrides.pop(get_user_from_token)


@pytest.fixture
async def _setup_db():
    client = AsyncMongoMockClient()
    await init_beanie(
        document_models=doc_models(),
        database=client.get_database(name="unit_test_db"),
    )

    yield

    await client.drop_database("unit_test_db")


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
