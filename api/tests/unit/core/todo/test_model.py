from app.core.todo import model as uut
from tests.factories.todo_factory import (
    TodoCreateFactory,
    TodoFactory,
    TodoListCreateFactory,
    TodoListFactory,
    TodoListUpdateFactory,
    TodoUpdateFactory,
)


def test_TodoList():
    todo_list = TodoListFactory.build()

    expected = todo_list

    actual = uut.TodoList(**todo_list.dict())

    assert actual == expected


def test_TodoList_defaults():
    todo_list = TodoListFactory.build()

    expected = uut.TodoList(**todo_list.dict())
    expected.date_modified = None

    actual = uut.TodoList(**todo_list.dict(exclude={"date_modified"}))

    assert actual == expected


def test_TodoListCreate():
    todo_list_create = TodoListCreateFactory.build()

    expected = todo_list_create

    actual = uut.TodoListCreate(**todo_list_create.dict())

    assert actual == expected


def test_TodoListUpdate():
    todo_list_update = TodoListUpdateFactory.build()

    expected = todo_list_update

    actual = uut.TodoListUpdate(**todo_list_update.dict())

    assert actual == expected


def test_TodoListUpdate_defaults():
    todo_list_update = TodoListUpdateFactory.build()

    expected = uut.TodoListUpdate(**todo_list_update.dict())
    expected.list_name = None

    actual = uut.TodoListUpdate()

    assert actual == expected


def test_Todo():
    todo = TodoFactory.build()

    expected = todo

    actual = uut.Todo(**todo.dict())

    assert actual == expected


def test_Todo_defaults():
    todo = TodoFactory.build()

    expected = uut.Todo(**todo.dict())
    expected.date_modified = None

    actual = uut.Todo(**todo.dict(exclude={"date_modified"}))

    assert actual == expected


def test_TodoCreate():
    todo_create = TodoCreateFactory.build()

    expected = todo_create

    actual = uut.TodoCreate(**todo_create.dict())

    assert actual == expected


def test_TodoUpdate():
    todo_update = TodoUpdateFactory.build()

    expected = todo_update

    actual = uut.TodoUpdate(**todo_update.dict())

    assert actual == expected


def test_TodoUpdate_defaults():
    todo_update = TodoUpdateFactory.build()

    expected = uut.TodoUpdate(**todo_update.dict())
    expected.todo_list_id = None
    expected.description = None
    expected.completed = None

    actual = uut.TodoUpdate()

    assert actual == expected
