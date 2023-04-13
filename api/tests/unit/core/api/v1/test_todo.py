from unittest.mock import AsyncMock

from tests.factories.todo_factory import (
    TodoCreateFactory,
    TodoFactory,
    TodoListCreateFactory,
    TodoListFactory,
    TodoListUpdateFactory,
    TodoUpdateFactory,
)
from tests.util import json_dict

UUT_PATH = "app.core.api.v1.todo"


def test_create_todo_list(client, mocker, auth_headers, override_get_user_from_token):
    todo_list_create = TodoListCreateFactory.build()
    todo_list = TodoListFactory.build(
        username=override_get_user_from_token.username, **todo_list_create.dict()
    )

    expected = json_dict(todo_list.dict())

    mocker.patch(
        f"{UUT_PATH}.todo_service.create_todo_list", AsyncMock(return_value=todo_list)
    )

    actual = client.post(
        "/api/v1/todo/list", headers=auth_headers, data=todo_list_create.json()
    )

    assert actual.status_code == 200
    assert actual.json() == expected


def test_fetch_todo_lists(client, mocker, auth_headers, override_get_user_from_token):
    todo_list_1 = TodoListFactory.build(username=override_get_user_from_token.username)
    todo_list_2 = TodoListFactory.build(username=override_get_user_from_token.username)

    expected = json_dict([todo_list_1.dict(), todo_list_2.dict()])

    mocker.patch(
        f"{UUT_PATH}.todo_service.fetch_todo_lists",
        AsyncMock(return_value=[todo_list_1, todo_list_2]),
    )

    actual = client.get("/api/v1/todo/list", headers=auth_headers)

    assert actual.status_code == 200
    assert actual.json() == expected


def test_update_todo_list(client, mocker, auth_headers, override_get_user_from_token):
    todo_list_update = TodoListUpdateFactory.build()
    todo_list = TodoListFactory.build(
        username=override_get_user_from_token.username, **todo_list_update.dict()
    )

    expected = json_dict(todo_list.dict())

    mocker.patch(
        f"{UUT_PATH}.todo_service.update_todo_list", AsyncMock(return_value=todo_list)
    )

    actual = client.put(
        f"/api/v1/todo/list/{todo_list.todo_list_id}",
        headers=auth_headers,
        data=todo_list_update.json(),
    )

    assert actual.status_code == 200
    assert actual.json() == expected


def test_delete_todo_list(client, mocker, auth_headers, override_get_user_from_token):
    todo_list = TodoListFactory.build(username=override_get_user_from_token.username)

    expected = json_dict(todo_list.dict())

    mocker.patch(
        f"{UUT_PATH}.todo_service.delete_todo_list", AsyncMock(return_value=todo_list)
    )

    actual = client.delete(
        f"/api/v1/todo/list/{todo_list.todo_list_id}", headers=auth_headers
    )

    assert actual.status_code == 200
    assert actual.json() == expected


def test_create_todo(client, mocker, auth_headers, override_get_user_from_token):
    todo_create = TodoCreateFactory.build()
    todo = TodoFactory.build(
        username=override_get_user_from_token.username, **todo_create.dict()
    )

    expected = json_dict(todo.dict())

    mocker.patch(f"{UUT_PATH}.todo_service.create_todo", AsyncMock(return_value=todo))

    actual = client.post(
        "/api/v1/todo/task", headers=auth_headers, data=todo_create.json()
    )

    assert actual.status_code == 200
    assert actual.json() == expected


def test_fetch_todos(client, mocker, auth_headers, override_get_user_from_token):
    todo_1 = TodoFactory.build(username=override_get_user_from_token.username)
    todo_2 = TodoFactory.build(username=override_get_user_from_token.username)

    expected = json_dict([todo_1.dict(), todo_2.dict()])

    mocker.patch(
        f"{UUT_PATH}.todo_service.fetch_todos", AsyncMock(return_value=[todo_1, todo_2])
    )

    actual = client.get("/api/v1/todo/task", headers=auth_headers)

    assert actual.status_code == 200
    assert actual.json() == expected


def test_fetch_todos_from_list(
    client, mocker, auth_headers, override_get_user_from_token
):
    todo_1 = TodoFactory.build(username=override_get_user_from_token.username)
    todo_2 = TodoFactory.build(
        username=override_get_user_from_token.username, todo_list_id=todo_1.todo_list_id
    )

    expected = json_dict([todo_1.dict(), todo_2.dict()])

    mocker.patch(
        f"{UUT_PATH}.todo_service.fetch_todos", AsyncMock(return_value=[todo_1, todo_2])
    )

    actual = client.get(
        f"/api/v1/todo/task?todo_list_id={todo_1.todo_list_id}",
        headers=auth_headers,
    )

    assert actual.status_code == 200
    assert actual.json() == expected


def test_fetch_todos_incomplete(
    client, mocker, auth_headers, override_get_user_from_token
):
    todo_1 = TodoFactory.build(
        username=override_get_user_from_token.username, completed=False
    )
    todo_2 = TodoFactory.build(
        username=override_get_user_from_token.username, completed=False
    )

    expected = json_dict([todo_1.dict(), todo_2.dict()])

    mocker.patch(
        f"{UUT_PATH}.todo_service.fetch_todos", AsyncMock(return_value=[todo_1, todo_2])
    )

    actual = client.get(
        "/api/v1/todo/task?incomplete_only=true",
        headers=auth_headers,
    )

    assert actual.status_code == 200
    assert actual.json() == expected


def test_update_todo(client, mocker, auth_headers, override_get_user_from_token):
    todo_update = TodoUpdateFactory.build()
    todo = TodoFactory.build(
        username=override_get_user_from_token.username, **todo_update.dict()
    )

    expected = json_dict(todo.dict())

    mocker.patch(f"{UUT_PATH}.todo_service.update_todo", AsyncMock(return_value=todo))

    actual = client.put(
        f"/api/v1/todo/task/{todo.todo_id}", headers=auth_headers, data=todo.json()
    )

    assert actual.status_code == 200
    assert actual.json() == expected


def test_delete_todo(client, mocker, auth_headers, override_get_user_from_token):
    todo = TodoFactory.build(username=override_get_user_from_token.username)

    expected = json_dict(todo.dict())

    mocker.patch(f"{UUT_PATH}.todo_service.delete_todo", AsyncMock(return_value=todo))

    actual = client.delete(f"/api/v1/todo/task/{todo.todo_id}", headers=auth_headers)

    assert actual.status_code == 200
    assert actual.json() == expected
