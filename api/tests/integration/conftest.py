import jwt
import pytest
from beanie import init_beanie
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient

from app.core.db.initialize import doc_models
from app.core.user.model import UserPublic
from app.main import app
from tests import util
from tests.factories.user_factory import UserDbFactory


@pytest.fixture
async def _setup_db():
    client = AsyncMongoMockClient()
    await init_beanie(
        document_models=doc_models(),
        database=client.get_database(name="integration_test_db"),
    )

    yield

    await client.drop_database("integration_test_db")


@pytest.fixture
def client(_setup_db):
    return TestClient(app)


@pytest.fixture
async def created_user():
    return await UserDbFactory.create(created=True)


@pytest.fixture
async def login_auth_token(client, created_user):
    credential = {
        "username": created_user.username,
        "password": "password",
    }
    response = client.post("/api/v1/auth/login", data=credential)

    assert response.status_code == 200

    return response.json()


@pytest.fixture
def headers_access_token(login_auth_token):
    return util.authorization_header(login_auth_token["access_token"])


@pytest.fixture
def token_data(login_auth_token):
    data = jwt.decode(
        login_auth_token["access_token"], options={"verify_signature": False}
    )
    return data


@pytest.fixture
def user_access_token(token_data):
    return UserPublic(**token_data["data"])


@pytest.fixture
def token_id(token_data):
    return token_data["token_id"]
