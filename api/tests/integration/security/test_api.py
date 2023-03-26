import pytest

from tests.factories.server_response_factory import ServerResponseFactory
from tests.factories.token_factory import AuthTokenFactory
from tests.util import authorization_header

api_data = [
    ("read current user", "GET", "/api/v1/user"),
    ("update current user", "PUT", "/api/v1/user"),
    ("create todo list", "POST", "/api/v1/todo/list"),
    ("fetch todo lists", "GET", "/api/v1/todo/list"),
    ("update todo list", "PUT", "/api/v1/todo/list/some_todo_list_id"),
    ("delete todo list", "DELETE", "/api/v1/todo/list/some_todo_list_id"),
    ("create todo", "POST", "/api/v1/todo/task"),
    ("fetch todos", "GET", "/api/v1/todo/task"),
    ("update todo", "PUT", "/api/v1/todo/task/some_todo_list_id"),
    ("delete todo", "DELETE", "/api/v1/todo/task/some_todo_list_id"),
]


@pytest.mark.parametrize("_description,method,endpoint", api_data)
async def test_api_expired_token(_description, method, endpoint, client):
    auth_token = AuthTokenFactory.build(jan_01_2020=True)
    headers = authorization_header(auth_token.access_token)

    expected = ServerResponseFactory.build(
        message="Invalid token with claim 'ACCESS_TOKEN'"
    )

    request = client.build_request(method, endpoint, headers=headers)
    actual = client.send(request)
    actual.json()

    assert actual.status_code == 401
    assert actual.json() == expected


@pytest.mark.parametrize("_description,method,endpoint", api_data)
async def test_api_invalid_token(
    _description,
    method,
    endpoint,
    client,
    login_auth_token,
):
    headers = authorization_header(login_auth_token["refresh_token"])

    expected = ServerResponseFactory.build(
        message="Token claim 'REFRESH_TOKEN' didn't match expected claim 'ACCESS_TOKEN'"
    )

    request = client.build_request(method, endpoint, headers=headers)

    actual = client.send(request)
    actual.json()

    assert actual.status_code == 401
    assert actual.json() == expected


@pytest.mark.parametrize("_description,method,endpoint", api_data)
async def test_api_no_token(_description, method, endpoint, client):
    expected = ServerResponseFactory.build(message="Not authenticated")

    request = client.build_request(method, endpoint)

    actual = client.send(request)
    actual.json()

    assert actual.status_code == 401
    assert actual.json() == expected


# todo: impl
async def test_api_user_disabled():
    pass
