from unittest.mock import AsyncMock

from app.core.todo import service as uut
from tests.factories.todo_factory import (
    TodoCreateFactory,
    TodoFactory,
    TodoListCreateFactory,
    TodoListFactory,
    TodoListUpdateFactory,
    TodoUpdateFactory,
)


async def test_create_todo_list(mocker):
    todo_list = TodoListFactory.build()
    todo_list_create = TodoListCreateFactory.build(**todo_list.dict())

    expected = todo_list

    mocker.patch(
        "app.core.todo.service.todo_repo.create_todo_list",
        AsyncMock(return_value=todo_list),
    )

    actual = await uut.create_todo_list(
        username="tester", todo_list_create=todo_list_create
    )

    assert actual == expected


async def test_fetch_todo_lists(mocker):
    todo_list = TodoListFactory.build()

    expected = [todo_list]

    mocker.patch(
        "app.core.todo.service.todo_repo.fetch_todo_lists",
        AsyncMock(return_value=[todo_list]),
    )

    actual = await uut.fetch_todo_lists("tester")

    assert actual == expected


async def test_update_todo_list(mocker):
    todo_list = TodoListFactory.build()
    todo_list_update = TodoListUpdateFactory.build(**todo_list.dict())

    expected = todo_list

    mocker.patch(
        "app.core.todo.service.todo_repo.update_todo_list",
        AsyncMock(return_value=todo_list),
    )

    actual = await uut.update_todo_list(
        username="username",
        todo_list_id=todo_list.todo_list_id,
        todo_list_update=todo_list_update,
    )

    assert actual == expected


async def test_delete_todo_list(mocker):
    todo_list = TodoListFactory.build()

    expected = todo_list

    mocker.patch(
        "app.core.todo.service.todo_repo.delete_todo_list",
        AsyncMock(return_value=todo_list),
    )

    actual = await uut.delete_todo_list(
        username="tester", todo_list_id=todo_list.todo_list_id
    )

    assert actual == expected


async def test_create_todo(mocker):
    todo_create = TodoCreateFactory.build()
    todo = TodoFactory.build(**todo_create.dict())

    expected = todo

    mocker.patch(
        "app.core.todo.service.todo_repo.create_todo", AsyncMock(return_value=todo)
    )

    actual = await uut.create_todo(username="tester", todo_create=todo_create)

    assert actual == expected


async def test_fetch_todos(mocker):
    todo = TodoFactory.build()

    expected = [todo]

    mocker.patch(
        "app.core.todo.service.todo_repo.fetch_todos", AsyncMock(return_value=[todo])
    )

    actual = await uut.fetch_todos(username="tester")

    assert actual == expected


async def test_fetch_todos_for_list_incomplete(mocker):
    todo = TodoFactory.build(completed=False)

    expected = [todo]

    mocker.patch(
        "app.core.todo.service.todo_repo.fetch_todos", AsyncMock(return_value=[todo])
    )

    actual = await uut.fetch_todos(
        username="tester", todo_list_id=todo.todo_list_id, incomplete_only=True
    )

    assert actual == expected


async def test_update_todo(mocker):
    todo_update = TodoUpdateFactory.build()
    todo = TodoFactory.build(**todo_update.dict())

    expected = todo

    mocker.patch(
        "app.core.todo.service.todo_repo.update_todo", AsyncMock(return_value=todo)
    )

    actual = await uut.update_todo(
        username="tester", todo_id=todo.todo_id, todo_update=todo_update
    )

    assert actual == expected


async def test_delete_todo(mocker):
    todo = TodoFactory.build()

    expected = todo

    mocker.patch(
        "app.core.todo.service.todo_repo.delete_todo", AsyncMock(return_value=todo)
    )

    actual = await uut.delete_todo(username="tester", todo_id=todo.todo_id)

    assert actual == expected
