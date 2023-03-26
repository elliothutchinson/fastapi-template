from datetime import datetime, timedelta, timezone

import pytest

from app.core.todo.model import Todo, TodoList
from tests.factories.server_response_factory import ServerResponseFactory
from tests.factories.todo_factory import (
    TodoCreateFactory,
    TodoDbFactory,
    TodoFactory,
    TodoListCreateFactory,
    TodoListDbFactory,
    TodoListFactory,
    TodoListUpdateFactory,
    TodoUpdateFactory,
)
from tests.util import json_dict


@pytest.fixture
async def todo_data(user_access_token):
    todo_list_db_1 = await TodoListDbFactory.create(username=user_access_token.username)
    todo_list_db_2 = await TodoListDbFactory.create(username=user_access_token.username)
    todo_db_1 = await TodoDbFactory.create(
        username=user_access_token.username,
        todo_list_id=todo_list_db_1.todo_list_id,
        completed=True,
    )
    todo_db_2 = await TodoDbFactory.create(
        username=user_access_token.username,
        todo_list_id=todo_list_db_2.todo_list_id,
        completed=False,
    )

    return [Todo(**todo_db_1.dict()).dict(), Todo(**todo_db_2.dict()).dict()]


async def test_create_todo_list(client, headers_access_token):
    todo_list_create = TodoListCreateFactory.build()

    expected = json_dict(
        TodoListFactory.build(created=True, **todo_list_create.dict()).dict(
            exclude={"date_created"}
        )
    )

    actual = client.post(
        "/api/v1/todo/list", headers=headers_access_token, data=todo_list_create.json()
    )
    actual_json = actual.json()
    actual_date_created = datetime.fromisoformat(actual_json.pop("date_created"))

    assert actual.status_code == 200
    assert actual_date_created > datetime.now(timezone.utc) - timedelta(seconds=5)
    assert actual_json == expected


async def test_create_todo_list_already_exists(client, headers_access_token):
    todo_list_db = await TodoListDbFactory.create()
    todo_list_create = TodoListCreateFactory.build(
        todo_list_id=todo_list_db.todo_list_id
    )

    expected = ServerResponseFactory.build(
        message=f"Todo list resource already exists with id '{todo_list_create.todo_list_id}'"  # pylint: disable=line-too-long
    )

    actual = client.post(
        "/api/v1/todo/list", headers=headers_access_token, data=todo_list_create.json()
    )

    assert actual.status_code == 409
    assert actual.json() == expected


async def test_fetch_todo_lists(client, headers_access_token, user_access_token):
    todo_list_db_1 = await TodoListDbFactory.create(username=user_access_token.username)
    todo_list_db_2 = await TodoListDbFactory.create(username=user_access_token.username)

    expected = json_dict(
        [
            TodoList(**todo_list_db_1.dict()).dict(),
            TodoList(**todo_list_db_2.dict()).dict(),
        ]
    )

    actual = client.get("/api/v1/todo/list", headers=headers_access_token)

    assert actual.status_code == 200
    assert actual.json() == expected


# todo: fetch and get updated todo list
async def test_update_todo_list(client, headers_access_token, user_access_token):
    todo_list_db = await TodoListDbFactory.create(username=user_access_token.username)
    todo_list_update = TodoListUpdateFactory.build()
    todo_list_dict = todo_list_db.dict() | todo_list_update.dict()

    expected = json_dict(TodoList(**todo_list_dict).dict(exclude={"date_modified"}))

    actual = client.put(
        f"/api/v1/todo/list/{todo_list_db.todo_list_id}",
        headers=headers_access_token,
        data=todo_list_update.json(),
    )
    actual_json = actual.json()
    actual_date_modified = datetime.fromisoformat(actual_json.pop("date_modified"))

    assert actual.status_code == 200
    assert actual_date_modified > datetime.now(timezone.utc) - timedelta(seconds=5)
    assert actual_json == expected


async def test_update_todo_list_not_exists(
    client, headers_access_token, user_access_token
):
    todo_list = TodoListFactory.build(username=user_access_token.username)
    todo_list_update = TodoListUpdateFactory.build()

    expected = ServerResponseFactory.build(
        message=f"Todo list resource not found with id '{todo_list.todo_list_id}'"
    )

    actual = client.put(
        f"/api/v1/todo/list/{todo_list.todo_list_id}",
        headers=headers_access_token,
        data=todo_list_update.json(),
    )

    assert actual.status_code == 404
    assert actual.json() == expected


# todo: fetch and verify removed
async def test_delete_todo_list(client, headers_access_token, user_access_token):
    todo_list_db = await TodoListDbFactory.create(username=user_access_token.username)

    expected = json_dict(TodoList(**todo_list_db.dict()).dict())

    actual = client.delete(
        f"/api/v1/todo/list/{todo_list_db.todo_list_id}",
        headers=headers_access_token,
    )

    assert actual.status_code == 200
    assert actual.json() == expected


async def test_delete_todo_list_not_exists(
    client, headers_access_token, user_access_token
):
    todo_list = TodoListFactory.build(username=user_access_token.username)

    expected = ServerResponseFactory.build(
        message=f"Todo list resource not found with id '{todo_list.todo_list_id}'"
    )

    actual = client.delete(
        f"/api/v1/todo/list/{todo_list.todo_list_id}",
        headers=headers_access_token,
    )

    assert actual.status_code == 404
    assert actual.json() == expected


async def test_delete_todo_list_deletes_todos(
    client, headers_access_token, user_access_token
):
    todo_list_db = await TodoListDbFactory.create(username=user_access_token.username)
    await TodoDbFactory.create(
        username=user_access_token.username, todo_list_id=todo_list_db.todo_list_id
    )

    expected = []

    response = client.delete(
        f"/api/v1/todo/list/{todo_list_db.todo_list_id}",
        headers=headers_access_token,
    )
    assert response.status_code == 200

    actual = client.get(
        f"/api/v1/todo/task?todo_list_id={todo_list_db.todo_list_id}",
        headers=headers_access_token,
    )

    assert actual.status_code == 200
    assert actual.json() == expected


async def test_create_todo(client, headers_access_token, user_access_token):
    todo_list_db = await TodoListDbFactory.create(username=user_access_token.username)
    todo_create = TodoCreateFactory.build(todo_list_id=todo_list_db.todo_list_id)

    expected = json_dict(
        TodoFactory.build(created=True, **todo_create.dict()).dict(
            exclude={"date_created"}
        )
    )

    actual = client.post(
        "/api/v1/todo/task", headers=headers_access_token, data=todo_create.json()
    )
    actual_json = actual.json()
    actual_date_created = datetime.fromisoformat(actual_json.pop("date_created"))

    assert actual.status_code == 200
    assert actual_date_created > datetime.now(timezone.utc) - timedelta(seconds=5)
    assert actual_json == expected


async def test_create_todo_already_exists(
    client, headers_access_token, user_access_token
):
    todo_list_db = await TodoListDbFactory.create(username=user_access_token.username)
    todo_db = await TodoDbFactory.create(
        username=user_access_token.username, todo_list_id=todo_list_db.todo_list_id
    )
    todo_create = TodoCreateFactory.build(**todo_db.dict())

    expected = ServerResponseFactory.build(
        message=f"Todo resource already exists with id '{todo_db.todo_id}'"
    )

    actual = client.post(
        "/api/v1/todo/task", headers=headers_access_token, data=todo_create.json()
    )

    assert actual.status_code == 409
    assert actual.json() == expected


async def test_create_todo_not_exist_list(
    client, headers_access_token, user_access_token
):
    todo_list = TodoListFactory.build(username=user_access_token.username)
    todo_create = TodoCreateFactory.build(todo_list_id=todo_list.todo_list_id)

    expected = ServerResponseFactory.build(
        message=f"Todo list resource not found with id '{todo_list.todo_list_id}'"
    )

    actual = client.post(
        "/api/v1/todo/task", headers=headers_access_token, data=todo_create.json()
    )

    assert actual.status_code == 409
    assert actual.json() == expected


async def test_fetch_todos(client, headers_access_token, todo_data):
    expected = json_dict(todo_data)

    actual = client.get("/api/v1/todo/task", headers=headers_access_token)

    assert actual.status_code == 200
    assert actual.json() == expected


async def test_fetch_todos_not_exists(client, headers_access_token):
    expected = []

    actual = client.get("/api/v1/todo/task", headers=headers_access_token)

    assert actual.status_code == 200
    assert actual.json() == expected


async def test_fetch_todos_for_list(client, headers_access_token, todo_data):
    todo_1, *_ = todo_data
    expected = json_dict([todo_1])

    actual = client.get(
        f"/api/v1/todo/task?todo_list_id={todo_1['todo_list_id']}",
        headers=headers_access_token,
    )

    assert actual.status_code == 200
    assert actual.json() == expected


async def test_fetch_todos_incomplete_only(client, headers_access_token, todo_data):
    _, todo_2, *_ = todo_data
    expected = json_dict([todo_2])

    actual = client.get(
        "/api/v1/todo/task?incomplete_only=true",
        headers=headers_access_token,
    )

    assert actual.status_code == 200
    assert actual.json() == expected


async def test_fetch_todos_incomplete_only_false(
    client, headers_access_token, todo_data
):
    expected = json_dict(todo_data)

    actual = client.get(
        "/api/v1/todo/task?incomplete_only=false", headers=headers_access_token
    )

    assert actual.status_code == 200
    assert actual.json() == expected


# todo: fetch and get updated todo
async def test_update_todo(client, headers_access_token, user_access_token):
    todo_list_db_1 = await TodoListDbFactory.create(username=user_access_token.username)
    todo_list_db_2 = await TodoListDbFactory.create(username=user_access_token.username)
    todo_db = await TodoDbFactory.create(
        username=user_access_token.username,
        todo_list_id=todo_list_db_1.todo_list_id,
    )
    todo_update = TodoUpdateFactory.build(todo_list_id=todo_list_db_2.todo_list_id)
    todo_dict = todo_db.dict() | todo_update.dict()

    expected = json_dict(Todo(**todo_dict).dict(exclude={"date_modified"}))

    actual = client.put(
        f"/api/v1/todo/task/{todo_db.todo_id}",
        headers=headers_access_token,
        data=todo_update.json(),
    )
    actual_json = actual.json()
    actual_date_modified = datetime.fromisoformat(actual_json.pop("date_modified"))

    assert actual.status_code == 200
    assert actual_date_modified > datetime.now(timezone.utc) - timedelta(seconds=5)
    assert actual_json == expected


async def test_update_todo_not_exists(client, headers_access_token, user_access_token):
    todo_list_db_1 = await TodoListDbFactory.create(username=user_access_token.username)
    todo_list_db_2 = await TodoListDbFactory.create(username=user_access_token.username)
    todo = TodoFactory.build(
        username=user_access_token.username,
        todo_list_id=todo_list_db_1.todo_list_id,
    )
    todo_update = TodoUpdateFactory.build(todo_list_id=todo_list_db_2.todo_list_id)

    expected = ServerResponseFactory.build(
        message=f"Todo resource not found with id '{todo.todo_id}'"
    )

    actual = client.put(
        f"/api/v1/todo/task/{todo.todo_id}",
        headers=headers_access_token,
        data=todo_update.json(),
    )

    assert actual.status_code == 404
    assert actual.json() == expected


async def test_update_todo_not_exists_list(
    client, headers_access_token, user_access_token
):
    todo_list_db_1 = await TodoListDbFactory.create(username=user_access_token.username)
    todo_list_2 = TodoListFactory.build(username=user_access_token.username)
    todo_db = await TodoDbFactory.create(
        username=user_access_token.username,
        todo_list_id=todo_list_db_1.todo_list_id,
    )
    todo_update = TodoUpdateFactory.build(todo_list_id=todo_list_2.todo_list_id)

    expected = ServerResponseFactory.build(
        message=f"Todo list resource not found with id '{todo_list_2.todo_list_id}'"
    )

    actual = client.put(
        f"/api/v1/todo/task/{todo_db.todo_id}",
        headers=headers_access_token,
        data=todo_update.json(),
    )

    assert actual.status_code == 409
    assert actual.json() == expected


async def test_delete_todo(client, headers_access_token, todo_data):
    todo_1, *_ = todo_data
    expected = json_dict(todo_1)

    actual = client.delete(
        f"/api/v1/todo/task/{todo_1['todo_id']}", headers=headers_access_token
    )

    assert actual.status_code == 200
    assert actual.json() == expected


async def test_delete_todo_deletes_todo(client, headers_access_token, todo_data):
    todo_1, todo_2, *_ = todo_data
    expected = json_dict([todo_2])

    response = client.delete(
        f"/api/v1/todo/task/{todo_1['todo_id']}", headers=headers_access_token
    )
    assert response.status_code == 200

    actual = client.get("/api/v1/todo/task", headers=headers_access_token)

    assert actual.status_code == 200
    assert actual.json() == expected


async def test_delete_todo_not_exists(client, headers_access_token, user_access_token):
    todo = TodoFactory.build(username=user_access_token.username)

    expected = ServerResponseFactory.build(
        message=f"Todo resource not found with id '{todo.todo_id}'"
    )

    actual = client.delete(
        f"/api/v1/todo/task/{todo.todo_id}", headers=headers_access_token
    )

    assert actual.status_code == 404
    assert actual.json() == expected
