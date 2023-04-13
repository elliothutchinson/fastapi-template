from datetime import datetime, timezone

import pytest
from freezegun import freeze_time

from app.core.exception import DataConflictException, ResourceNotFoundException
from app.core.todo import repo as uut
from app.core.todo.model import Todo, TodoList, TodoListUpdate, TodoUpdate
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


def test_TodoListDb(_setup_db):
    todo_list_db = TodoListDbFactory.build()

    expected = todo_list_db

    actual = uut.TodoListDb(**todo_list_db.dict())

    assert actual == expected


def test_TodoListDb_defaults(_setup_db):
    todo_list_db = TodoListDbFactory.build()

    expected = uut.TodoListDb(**todo_list_db.dict())
    expected.date_modified = None

    actual = uut.TodoListDb(**todo_list_db.dict(exclude={"date_modified"}))

    assert actual == expected


def test_TodoDb(_setup_db):
    todo_db = TodoDbFactory.build()

    expected = todo_db

    actual = uut.TodoDb(**todo_db.dict())

    assert actual == expected


def test_TodoDb_defaults(_setup_db):
    todo_db = TodoDbFactory.build()

    expected = uut.TodoDb(**todo_db.dict())
    expected.date_modified = None

    actual = uut.TodoDb(**todo_db.dict(exclude={"date_modified"}))

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_create_todo_list(_setup_db):
    todo_list_create = TodoListCreateFactory.build()
    todo_list = TodoListFactory.build(
        **todo_list_create.dict(),
        created=True,
        date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
    )

    expected = todo_list

    actual = await uut.create_todo_list(
        username="tester", todo_list_create=todo_list_create
    )

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_create_todo_list_already_exists(_setup_db):
    todo_list_db = await TodoListDbFactory.create(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )
    todo_list_create = TodoListCreateFactory.build(**todo_list_db.dict())

    with pytest.raises(
        DataConflictException,
        match=f"Todo list resource already exists with id '{todo_list_create.todo_list_id}'",  # pylint: disable=line-too-long
    ):
        await uut.create_todo_list(
            username=todo_list_db.username, todo_list_create=todo_list_create
        )


async def test_fetch_todo_lists(_setup_db):
    todo_list_db = await TodoListDbFactory.create(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    expected = [TodoList(**todo_list_db.dict())]

    actual = await uut.fetch_todo_lists(username=todo_list_db.username)

    assert actual == expected


async def test_fetch_todo_lists_not_exists(_setup_db):
    expected = []

    actual = await uut.fetch_todo_lists(username="tester")

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_update_todo_list_all(_setup_db):
    todo_list_db = await TodoListDbFactory.create(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )
    todo_list_create = TodoListUpdateFactory.build()

    expected = TodoList(
        **todo_list_db.dict(exclude={"list_name"}), **todo_list_create.dict()
    )
    expected.date_modified = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)

    actual = await uut.update_todo_list(
        username=todo_list_db.username,
        todo_list_id=todo_list_db.todo_list_id,
        todo_list_update=todo_list_create,
    )

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_update_todo_list_none(_setup_db):
    todo_list_db = await TodoListDbFactory.create(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )
    todo_list_create = TodoListUpdate()

    expected = TodoList(**todo_list_db.dict())
    expected.date_modified = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)

    actual = await uut.update_todo_list(
        username=todo_list_db.username,
        todo_list_id=todo_list_db.todo_list_id,
        todo_list_update=todo_list_create,
    )

    assert actual == expected


async def test_update_todo_list_not_exists(_setup_db):
    todo_list_db = TodoListDbFactory.build(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )
    todo_list_create = TodoListUpdate()

    with pytest.raises(
        ResourceNotFoundException,
        match=f"Todo list resource not found with id '{todo_list_db.todo_list_id}'",
    ):
        await uut.update_todo_list(
            username=todo_list_db.username,
            todo_list_id=todo_list_db.todo_list_id,
            todo_list_update=todo_list_create,
        )


async def test_delete_todo_list(_setup_db):
    todo_list_db = await TodoListDbFactory.create(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    expected = TodoList(**todo_list_db.dict())

    actual = await uut.delete_todo_list(
        username=todo_list_db.username, todo_list_id=todo_list_db.todo_list_id
    )

    assert actual == expected


async def test_delete_todo_list_deletes_todos(_setup_db):
    todo_list_db = await TodoListDbFactory.create(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    todo_db_1 = await TodoDbFactory.create(
        username=todo_list_db.username,
    )
    await TodoDbFactory.create(
        todo_list_id=todo_list_db.todo_list_id,
        username=todo_list_db.username,
    )

    expected = [Todo(**todo_db_1.dict())]

    await uut.delete_todo_list(
        username=todo_list_db.username, todo_list_id=todo_list_db.todo_list_id
    )
    actual = await uut.fetch_todos(username=todo_list_db.username)

    assert actual == expected


async def test_delete_todo_list_not_exists(_setup_db):
    todo_list_db = TodoListDbFactory.build(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    with pytest.raises(
        ResourceNotFoundException,
        match=f"Todo list resource not found with id '{todo_list_db.todo_list_id}'",
    ):
        await uut.delete_todo_list(
            username=todo_list_db.username, todo_list_id=todo_list_db.todo_list_id
        )


async def test__validate_todo_list(_setup_db):
    todo_list_db = await TodoListDbFactory.create(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    expected = todo_list_db

    actual = await uut._validate_todo_list(  # pylint: disable=protected-access
        username=todo_list_db.username, todo_list_id=todo_list_db.todo_list_id
    )

    assert actual == expected


async def test__validate_todo_list_not_exists(_setup_db):
    todo_list_db = TodoListDbFactory.build(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    with pytest.raises(
        DataConflictException,
        match=f"Todo list resource not found with id '{todo_list_db.todo_list_id}'",
    ):
        await uut._validate_todo_list(  # pylint: disable=protected-access
            username=todo_list_db.username, todo_list_id=todo_list_db.todo_list_id
        )


@freeze_time("2020-01-01 00:00:00")
async def test_create_todo(_setup_db):
    todo_list_db = await TodoListDbFactory.create(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    todo = TodoFactory.build(
        todo_list_id=todo_list_db.todo_list_id,
        created=True,
        date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
    )
    todo_create = TodoCreateFactory.build(**todo.dict())

    expected = todo

    actual = await uut.create_todo(
        username=todo_list_db.username, todo_create=todo_create
    )

    assert actual == expected


async def test_create_todo_not_exists_list(_setup_db):
    todo_create = TodoCreateFactory.build()

    with pytest.raises(
        DataConflictException,
        match=f"Todo list resource not found with id '{todo_create.todo_list_id}'",
    ):
        await uut.create_todo(username="tester", todo_create=todo_create)


async def test_create_todo_already_exists(_setup_db):
    todo_list_db = await TodoListDbFactory.create(
        created=True, date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)
    )

    todo_db = await TodoDbFactory.create(
        username=todo_list_db.username,
        todo_list_id=todo_list_db.todo_list_id,
        created=True,
        date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
    )
    todo_create = TodoCreateFactory.build(**todo_db.dict())

    with pytest.raises(
        DataConflictException,
        match=f"Todo resource already exists with id '{todo_create.todo_id}'",
    ):
        await uut.create_todo(username=todo_list_db.username, todo_create=todo_create)


async def test_fetch_todos_all(_setup_db):
    todo_list_db_1 = await TodoListDbFactory.create()
    todo_list_db_2 = await TodoListDbFactory.create(username=todo_list_db_1.username)
    todo_db_1 = await TodoDbFactory.create(
        todo_list_id=todo_list_db_1.todo_list_id,
        username=todo_list_db_1.username,
        completed=True,
    )
    todo_db_2 = await TodoDbFactory.create(
        todo_list_id=todo_list_db_2.todo_list_id,
        username=todo_list_db_1.username,
        completed=False,
    )

    expected = [Todo(**todo_db_1.dict()), Todo(**todo_db_2.dict())]

    actual = await uut.fetch_todos(username=todo_list_db_1.username)

    assert actual == expected


async def test_fetch_todos_for_list(_setup_db):
    todo_list_db_1 = await TodoListDbFactory.create()
    todo_list_db_2 = await TodoListDbFactory.create(username=todo_list_db_1.username)
    todo_db_1 = await TodoDbFactory.create(
        todo_list_id=todo_list_db_1.todo_list_id,
        username=todo_list_db_1.username,
        completed=True,
    )
    await TodoDbFactory.create(
        todo_list_id=todo_list_db_2.todo_list_id,
        username=todo_list_db_1.username,
        completed=False,
    )

    expected = [Todo(**todo_db_1.dict())]

    actual = await uut.fetch_todos(
        username=todo_list_db_1.username, todo_list_id=todo_list_db_1.todo_list_id
    )

    assert actual == expected


async def test_fetch_todos_incomplete(_setup_db):
    todo_list_db_1 = await TodoListDbFactory.create()
    todo_list_db_2 = await TodoListDbFactory.create(username=todo_list_db_1.username)
    await TodoDbFactory.create(
        todo_list_id=todo_list_db_1.todo_list_id,
        username=todo_list_db_1.username,
        completed=True,
    )
    todo_db_2 = await TodoDbFactory.create(
        todo_list_id=todo_list_db_2.todo_list_id,
        username=todo_list_db_1.username,
        completed=False,
    )

    expected = [Todo(**todo_db_2.dict())]

    actual = await uut.fetch_todos(
        username=todo_list_db_1.username, incomplete_only=True
    )

    assert actual == expected


async def test_fetch_todos_for_list_incomplete(_setup_db):
    todo_list_db_1 = await TodoListDbFactory.create()
    todo_list_db_2 = await TodoListDbFactory.create(username=todo_list_db_1.username)
    await TodoDbFactory.create(
        todo_list_id=todo_list_db_1.todo_list_id,
        username=todo_list_db_1.username,
        completed=True,
    )
    todo_db_2 = await TodoDbFactory.create(
        todo_list_id=todo_list_db_2.todo_list_id,
        username=todo_list_db_1.username,
        completed=False,
    )
    await TodoDbFactory.create(
        todo_list_id=todo_list_db_2.todo_list_id,
        username=todo_list_db_1.username,
        completed=True,
    )

    expected = [Todo(**todo_db_2.dict())]

    actual = await uut.fetch_todos(
        username=todo_list_db_1.username,
        todo_list_id=todo_list_db_2.todo_list_id,
        incomplete_only=True,
    )

    assert actual == expected


async def test_fetch_todos_not_exists(_setup_db):
    todo_list_db_1 = TodoListDbFactory.build()

    expected = []

    actual = await uut.fetch_todos(username=todo_list_db_1.username)

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_update_todo_all(_setup_db):
    todo_list_db_1 = await TodoListDbFactory.create()
    todo_list_db_2 = await TodoListDbFactory.create(username=todo_list_db_1.username)
    todo_db = await TodoDbFactory.create(
        todo_list_id=todo_list_db_1.todo_list_id,
        username=todo_list_db_1.username,
    )
    todo_update = TodoUpdateFactory.build(todo_list_id=todo_list_db_2.todo_list_id)

    expected = Todo(
        **todo_db.dict(exclude={"todo_list_id", "description", "completed"}),
        **todo_update.dict(),
    )
    expected.date_modified = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)

    actual = await uut.update_todo(
        username=todo_list_db_1.username,
        todo_id=todo_db.todo_id,
        todo_update=todo_update,
    )

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_update_todo_none(_setup_db):
    todo_list_db = await TodoListDbFactory.create()
    todo_db = await TodoDbFactory.create(
        todo_list_id=todo_list_db.todo_list_id,
        username=todo_list_db.username,
    )
    todo_update = TodoUpdate()

    expected = Todo(**todo_db.dict())
    expected.date_modified = datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc)

    actual = await uut.update_todo(
        username=todo_list_db.username, todo_id=todo_db.todo_id, todo_update=todo_update
    )

    assert actual == expected


@freeze_time("2020-01-01 00:00:00")
async def test_update_todo_not_exists(_setup_db):
    todo_list_db = await TodoListDbFactory.create()
    todo_db = TodoDbFactory.build()
    todo_update = TodoUpdate()

    with pytest.raises(
        ResourceNotFoundException,
        match=f"Todo resource not found with id '{todo_db.todo_id}'",
    ):
        await uut.update_todo(
            username=todo_list_db.username,
            todo_id=todo_db.todo_id,
            todo_update=todo_update,
        )


@freeze_time("2020-01-01 00:00:00")
async def test_update_todo_not_exists_list(_setup_db):
    todo_list_db_1 = await TodoListDbFactory.create()
    todo_list_db_2 = TodoListDbFactory.build(username=todo_list_db_1.username)
    todo_db = await TodoDbFactory.create(
        todo_list_id=todo_list_db_1.todo_list_id,
        username=todo_list_db_1.username,
    )
    todo_update = TodoUpdateFactory.build(todo_list_id=todo_list_db_2.todo_list_id)

    with pytest.raises(
        DataConflictException,
        match=f"Todo list resource not found with id '{todo_update.todo_list_id}'",
    ):
        await uut.update_todo(
            username=todo_list_db_1.username,
            todo_id=todo_db.todo_id,
            todo_update=todo_update,
        )


async def test_delete_todo(_setup_db):
    todo_list_db = await TodoListDbFactory.create()
    todo_db = await TodoDbFactory.create(
        todo_list_id=todo_list_db.todo_list_id,
        username=todo_list_db.username,
    )

    expected = Todo(**todo_db.dict())

    actual = await uut.delete_todo(
        username=todo_list_db.username, todo_id=todo_db.todo_id
    )

    assert actual == expected


async def test_delete_todo_not_exists(_setup_db):
    todo_list_db = await TodoListDbFactory.create()
    todo_db = TodoDbFactory.build(
        todo_list_id=todo_list_db.todo_list_id,
        username=todo_list_db.username,
    )

    with pytest.raises(
        ResourceNotFoundException,
        match=f"Todo resource not found with id '{todo_db.todo_id}'",
    ):
        await uut.delete_todo(username=todo_list_db.username, todo_id=todo_db.todo_id)
