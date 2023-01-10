from unittest.mock import Mock, patch

import orjson
import pytest

from app.core.todo.model import TodoList, TodoListUpdate, TodoUpdate


@pytest.fixture
def todo_list(todo_list_dict):

    return TodoList(**todo_list_dict)


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
def test_create_todo_list(
    _setup_db_user_db, _setup_cache, auth_headers, client, todo_list_create, todo_list
):
    expected_json = orjson.dumps(todo_list.dict()).decode()
    expected_json_dict = orjson.loads(expected_json)

    todo_list_create_json = orjson.dumps(todo_list_create.dict()).decode()
    todo_list_create_json_dict = orjson.loads(todo_list_create_json)

    actual = client.post(
        "/api/v1/todo/list", headers=auth_headers, json=todo_list_create_json_dict
    )
    actual_json = actual.json()

    assert actual.status_code == 200
    assert actual_json == expected_json_dict


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
def test_fetch_todo_lists(
    _setup_db_user_db,
    _setup_cache,
    auth_headers,
    client,
    _setup_db_todo_list_db,
    todo_list,
):
    expected_json = orjson.dumps([todo_list.dict()]).decode()
    expected_json_dict = orjson.loads(expected_json)

    actual = client.get("/api/v1/todo/list", headers=auth_headers)
    actual_json = actual.json()

    assert actual.status_code == 200
    assert actual_json == expected_json_dict


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
def test_update_todo_list(
    _setup_db_user_db,
    _setup_cache,
    auth_headers,
    client,
    _setup_db_todo_list_db,
    todo_list,
):
    todo_list.list_name = "yard"
    expected_json = orjson.dumps(todo_list.dict()).decode()
    expected_json_dict = orjson.loads(expected_json)

    todo_list_update = TodoListUpdate(list_name="yard")
    todo_list_update_json = orjson.dumps(todo_list_update.dict()).decode()
    todo_list_update_json_dict = orjson.loads(todo_list_update_json)

    actual = client.put(
        f"/api/v1/todo/list/{todo_list.todo_list_id}",
        headers=auth_headers,
        json=todo_list_update_json_dict,
    )
    actual_json = actual.json()

    assert actual.status_code == 200
    assert actual_json == expected_json_dict


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
def test_delete_todo_list(
    _setup_db_user_db,
    _setup_cache,
    auth_headers,
    client,
    _setup_db_todo_list_db,
    todo_list,
):
    expected_json = orjson.dumps(todo_list.dict()).decode()
    expected_json_dict = orjson.loads(expected_json)

    actual = client.delete(
        f"/api/v1/todo/list/{todo_list.todo_list_id}", headers=auth_headers
    )
    actual_json = actual.json()

    assert actual.status_code == 200
    assert actual_json == expected_json_dict


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
def test_create_todo(
    _setup_db_user_db,
    _setup_cache,
    auth_headers,
    client,
    _setup_db_todo_list_db,
    todo_create,
    todo,
):
    expected_json = orjson.dumps(todo.dict()).decode()
    expected_json_dict = orjson.loads(expected_json)

    todo_create_json = orjson.dumps(todo_create.dict()).decode()
    todo_create_json_dict = orjson.loads(todo_create_json)

    actual = client.post(
        "/api/v1/todo/task", headers=auth_headers, json=todo_create_json_dict
    )
    actual_json = actual.json()

    assert actual.status_code == 200
    assert actual_json == expected_json_dict


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
def test_fetch_todos(
    _setup_db_user_db,
    _setup_cache,
    auth_headers,
    client,
    _setup_db_todo_list_db,
    _setup_db_todo_db,
    todo,
):
    expected_json = orjson.dumps([todo.dict()]).decode()
    expected_json_dict = orjson.loads(expected_json)

    actual = client.get("/api/v1/todo/task", headers=auth_headers)
    actual_json = actual.json()

    assert actual.status_code == 200
    assert actual_json == expected_json_dict


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
def test_fetch_todos_filter(
    _setup_db_user_db,
    _setup_cache,
    auth_headers,
    client,
    _setup_db_todo_list_db,
    _setup_db_todo_db,
):
    expected = []

    actual = client.get(
        "/api/v1/todo/task?incomplete_only=true&todo_list_id=845aa33c-e1fd-4785-9fd9-4d23dd04cedf",  # pylint: disable=line-too-long
        headers=auth_headers,
    )
    actual_json = actual.json()

    assert actual.status_code == 200
    assert actual_json == expected


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
def test_update_todo(
    _setup_db_user_db,
    _setup_cache,
    auth_headers,
    client,
    _setup_db_todo_list_db,
    _setup_db_todo_db,
    todo,
):
    todo_update = TodoUpdate(
        description="walk dogs",
        completed=True,
    )

    expected_json = orjson.dumps(
        todo.dict() | todo_update.dict(exclude={"todo_list_id"})
    ).decode()
    expected_json_dict = orjson.loads(expected_json)

    todo_update_json = orjson.dumps(todo_update.dict()).decode()
    todo_update_json_dict = orjson.loads(todo_update_json)

    actual = client.put(
        f"/api/v1/todo/task/{todo.todo_id}",
        headers=auth_headers,
        json=todo_update_json_dict,
    )
    actual_json = actual.json()

    assert actual.status_code == 200
    assert actual_json == expected_json_dict


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
def test_delete_todo(
    _setup_db_user_db,
    _setup_cache,
    auth_headers,
    client,
    _setup_db_todo_list_db,
    _setup_db_todo_db,
    todo,
):
    expected_json = orjson.dumps(todo.dict()).decode()
    expected_json_dict = orjson.loads(expected_json)

    actual = client.delete(
        f"/api/v1/todo/task/{todo.todo_id}",
        headers=auth_headers,
    )
    actual_json = actual.json()

    assert actual.status_code == 200
    assert actual_json == expected_json_dict
