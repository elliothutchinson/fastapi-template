from datetime import datetime
from unittest.mock import Mock, patch
from uuid import UUID

import pytest

from app.core.exception import DataConflictException, ResourceNotFoundException
from app.core.todo import service as uut
from app.core.todo.model import TodoDb, TodoListDb, TodoListUpdate, TodoUpdate


@pytest.fixture
def todo_list_db(todo_list_dict):

    return TodoListDb(**todo_list_dict)


@pytest.fixture
def todo_db(todo_dict):

    return TodoDb(**todo_dict)


@pytest.fixture
async def todo_list_dbs(_setup_db, todo_list_db):

    return [
        await TodoListDb(**todo_list_db.dict()).save(),
        await TodoListDb(
            **todo_list_db.dict(exclude={"todo_list_id", "id"}),
            todo_list_id=UUID("c24819d4-d088-457f-85b4-d5a6642ec4bc"),
        ).save(),
        await TodoListDb(
            **todo_list_db.dict(exclude={"todo_list_id", "id", "username"}),
            todo_list_id=UUID("be82a9c8-ff38-4f7c-8934-3c90cb6894b8"),
            username="another_tester",
        ).save(),
    ]


@pytest.fixture
async def todo_dbs(_setup_db, todo_list_dbs, todo_db):

    return [
        await TodoDb(**todo_db.dict()).save(),
        await TodoDb(
            **todo_db.dict(exclude={"todo_id", "todo_list_id", "completed", "id"}),
            todo_id=UUID("5855c7ed-7f62-4827-a261-fceb03df429c"),
            todo_list_id=todo_list_dbs[1].todo_list_id,
            completed=True,
        ).save(),
        await TodoDb(
            **todo_db.dict(exclude={"todo_id", "todo_list_id", "id", "username"}),
            todo_id=UUID("74f8e3fb-1fe4-4888-b411-f974cbd6d96a"),
            todo_list_id=todo_list_dbs[2].todo_list_id,
            username="another_tester",
        ).save(),
    ]


@patch(
    "app.core.todo.service.datetime",
    Mock(now=Mock(return_value=datetime(2020, 1, 1, 0, 0))),
)
async def test_create_todo_list(_setup_db, todo_list_create, todo_list_dict):
    expected = todo_list_dict

    actual = await uut.create_todo_list(
        username="tester", todo_list_create=todo_list_create
    )
    actual_dict = actual.dict()
    actual_id = actual_dict.pop("id")

    assert actual_id is not None
    assert actual_dict == expected


async def test_create_todo_list_already_exists(
    _setup_db_todo_list_db, todo_list_create
):

    with pytest.raises(
        DataConflictException,
        match=f"Todo list resource already exists with id '{todo_list_create.todo_list_id}'",
    ):
        await uut.create_todo_list(username="tester", todo_list_create=todo_list_create)


async def test_fetch_todo_lists(_setup_db, todo_list_dbs):
    expected = todo_list_dbs
    expected.pop()

    actual = await uut.fetch_todo_lists("tester")

    assert len(actual) == 2
    assert actual == expected


@patch(
    "app.core.todo.service.datetime",
    Mock(now=Mock(return_value=datetime(2020, 1, 2, 0, 0))),
)
async def test_update_todo_list(_setup_db_todo_list_db, todo_list_dict):
    todo_list_update = TodoListUpdate(list_name="yard")

    expected = todo_list_dict.copy()
    expected["list_name"] = "yard"
    expected["date_modified"] = datetime(2020, 1, 2, 0, 0)

    actual = await uut.update_todo_list(
        username="tester",
        todo_list_id=todo_list_dict["todo_list_id"],
        todo_list_update=todo_list_update,
    )

    assert actual.dict(exclude={"id"}) == expected


@patch(
    "app.core.todo.service.datetime",
    Mock(now=Mock(return_value=datetime(2020, 1, 2, 0, 0))),
)
async def test_update_todo_list_empty_update(_setup_db_todo_list_db, todo_list_dict):
    todo_list_update = TodoListUpdate()

    expected = todo_list_dict.copy()
    expected["date_modified"] = datetime(2020, 1, 2, 0, 0)

    actual = await uut.update_todo_list(
        username="tester",
        todo_list_id=todo_list_dict["todo_list_id"],
        todo_list_update=todo_list_update,
    )

    assert actual.dict(exclude={"id"}) == expected


async def test_update_todo_list_not_exist(_setup_db, todo_list_dict):
    todo_list_update = TodoListUpdate(list_name="yard")

    with pytest.raises(
        ResourceNotFoundException,
        match=f"Todo list resource not found with id '{todo_list_dict['todo_list_id']}'",
    ):
        await uut.update_todo_list(
            username="tester",
            todo_list_id=todo_list_dict["todo_list_id"],
            todo_list_update=todo_list_update,
        )


async def test_delete_todo_list(_setup_db_todo_list_db, todo_list_dict):
    expected = todo_list_dict.copy()

    actual = await uut.delete_todo_list(
        username="tester",
        todo_list_id=todo_list_dict["todo_list_id"],
    )

    assert actual.dict(exclude={"id"}) == expected


async def test_delete_todo_list_not_exist(_setup_db, todo_list_dict):
    with pytest.raises(
        ResourceNotFoundException,
        match=f"Todo list resource not found with id '{todo_list_dict['todo_list_id']}'",
    ):
        await uut.delete_todo_list(
            username="tester",
            todo_list_id=todo_list_dict["todo_list_id"],
        )


async def test_validate_todo_list_valid(_setup_db_todo_list_db, todo_dict):
    actual = await uut.validate_todo_list(
        username="tester", todo_list_id=todo_dict["todo_list_id"]
    )

    assert actual is True


async def test_validate_todo_list_invalid(_setup_db, todo_dict):
    with pytest.raises(
        DataConflictException,
        match=f"Todo list resource not found with id '{todo_dict['todo_list_id']}'",
    ):
        await uut.validate_todo_list(
            username="tester", todo_list_id=todo_dict["todo_list_id"]
        )


@patch(
    "app.core.todo.service.datetime",
    Mock(now=Mock(return_value=datetime(2020, 1, 1, 0, 0))),
)
async def test_create_todo(_setup_db_todo_list_db, todo_create, todo_dict):
    expected = todo_dict

    actual = await uut.create_todo(username="tester", todo_create=todo_create)
    actual_dict = actual.dict()
    actual_id = actual_dict.pop("id")

    assert actual_id is not None
    assert actual_dict == expected


async def test_create_todo_already_exists(_setup_db_todo_db, todo_create):
    with pytest.raises(
        DataConflictException,
        match=f"Todo resource already exists with id '{todo_create.todo_id}'",
    ):
        await uut.create_todo(username="tester", todo_create=todo_create)


async def test_fetch_todos_todo_list_id_and_incomplete_only(todo_dbs):
    expected = []

    actual = await uut.fetch_todos(
        username="tester", todo_list_id=todo_dbs[1].todo_list_id, incomplete_only=True
    )

    assert actual == expected


async def test_fetch_todos_todo_list_id(todo_dbs):
    expected = [todo_dbs[1]]

    actual = await uut.fetch_todos(
        username="tester", todo_list_id=todo_dbs[1].todo_list_id
    )

    assert actual == expected


async def test_fetch_todos_incomplete_only(todo_dbs):
    expected = [todo_dbs[0]]

    actual = await uut.fetch_todos(username="tester", incomplete_only=True)

    assert actual == expected


async def test_fetch_todos_all(todo_dbs):
    expected = todo_dbs
    expected.pop()

    actual = await uut.fetch_todos(username="tester")

    assert actual == expected


@patch(
    "app.core.todo.service.datetime",
    Mock(now=Mock(return_value=datetime(2020, 1, 2, 0, 0))),
)
async def test_update_todo(_setup_db_todo_db, todo_list_db, todo_dict):
    todo_list = await TodoListDb(
        **todo_list_db.dict(exclude={"todo_list_id", "id"}),
        todo_list_id=UUID("c24819d4-d088-457f-85b4-d5a6642ec4bc"),
    ).save()

    todo_update = TodoUpdate(
        todo_list_id=todo_list_db.todo_list_id,
        description="walk dogs",
        completed=True,
    )

    expected = todo_dict.copy()
    expected.update(**todo_update.dict())
    expected["date_modified"] = datetime(2020, 1, 2, 0, 0)

    actual = await uut.update_todo(
        username="tester",
        todo_id=todo_dict["todo_id"],
        todo_update=todo_update,
    )

    assert actual.dict(exclude={"id"}) == expected


@patch(
    "app.core.todo.service.datetime",
    Mock(now=Mock(return_value=datetime(2020, 1, 2, 0, 0))),
)
async def test_update_todo_empty_update(_setup_db_todo_db, todo_dict):
    todo_update = TodoUpdate()

    expected = todo_dict.copy()
    expected["date_modified"] = datetime(2020, 1, 2, 0, 0)

    actual = await uut.update_todo(
        username="tester",
        todo_id=todo_dict["todo_id"],
        todo_update=todo_update,
    )

    assert actual.dict(exclude={"id"}) == expected


async def test_update_todo_not_exist(_setup_db, todo_dict):
    todo_update = TodoUpdate()

    with pytest.raises(
        ResourceNotFoundException,
        match=f"Todo resource not found with id '{todo_dict['todo_id']}'",
    ):
        await uut.update_todo(
            username="tester",
            todo_id=todo_dict["todo_id"],
            todo_update=todo_update,
        )


async def test_delete_todo(_setup_db_todo_db, todo_dict):
    expected = todo_dict.copy()

    actual = await uut.delete_todo(
        username="tester",
        todo_id=todo_dict["todo_id"],
    )

    assert actual.dict(exclude={"id"}) == expected


async def test_delete_todo_not_exist(_setup_db, todo_dict):
    with pytest.raises(
        ResourceNotFoundException,
        match=f"Todo resource not found with id '{todo_dict['todo_id']}'",
    ):
        await uut.delete_todo(
            username="tester",
            todo_id=todo_dict["todo_id"],
        )
