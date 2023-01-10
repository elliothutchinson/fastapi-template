from datetime import datetime
from uuid import UUID

from app.core.todo import model as uut


def test_TodoList():
    todo_list_dict = {
        "todo_list_id": UUID("7eb80ffa-b954-4c57-8fdf-5bc66fdc31de"),
        "list_name": "home",
    }

    expected = todo_list_dict

    actual = uut.TodoList(**todo_list_dict)

    assert actual.dict() == expected


def test_TodoListCreate():
    todo_list_dict = {
        "todo_list_id": UUID("7eb80ffa-b954-4c57-8fdf-5bc66fdc31de"),
        "list_name": "home",
    }

    expected = todo_list_dict

    actual = uut.TodoListCreate(**todo_list_dict)

    assert actual.dict() == expected


def test_TodoListUpdate_optional_fields():
    todo_list_dict = {}

    expected = {"list_name": None}

    actual = uut.TodoListUpdate(**todo_list_dict)

    assert actual.dict() == expected


def test_TodoListUpdate():
    todo_list_dict = {
        "list_name": "home",
    }

    expected = todo_list_dict

    actual = uut.TodoListUpdate(**todo_list_dict)

    assert actual.dict() == expected


def test_TodoListDb_optional_fields():
    todo_list_dict = {
        "todo_list_id": UUID("7eb80ffa-b954-4c57-8fdf-5bc66fdc31de"),
        "list_name": "home",
        "username": "tester",
        "date_created": datetime(2020, 1, 1, 0, 0),
    }

    expected = todo_list_dict
    expected["id"] = None
    expected["date_modified"] = None

    actual = uut.TodoListDb(**todo_list_dict)

    assert actual.dict() == expected


def test_TodoListDb():
    todo_list_dict = {
        "todo_list_id": UUID("7eb80ffa-b954-4c57-8fdf-5bc66fdc31de"),
        "list_name": "home",
        "username": "tester",
        "date_created": datetime(2020, 1, 1, 0, 0),
        "date_modified": datetime(2020, 1, 1, 0, 0),
    }

    expected = todo_list_dict
    expected["id"] = None

    actual = uut.TodoListDb(**todo_list_dict)

    assert actual.dict() == expected


def test_Todo():
    todo_dict = {
        "todo_id": UUID("bff1beef-79a6-45c4-984b-0af9f6d64675"),
        "todo_list_id": UUID("7eb80ffa-b954-4c57-8fdf-5bc66fdc31de"),
        "description": "wash dogs",
        "completed": False,
    }

    expected = todo_dict

    actual = uut.Todo(**todo_dict)

    assert actual.dict() == expected


def test_TodoCreate():
    todo_dict = {
        "todo_id": UUID("bff1beef-79a6-45c4-984b-0af9f6d64675"),
        "todo_list_id": UUID("7eb80ffa-b954-4c57-8fdf-5bc66fdc31de"),
        "description": "wash dogs",
        "completed": False,
    }

    expected = todo_dict

    actual = uut.TodoCreate(**todo_dict)

    assert actual.dict() == expected


def test_TodoUpdate_optional_fields():
    todo_dict = {}

    expected = {
        "todo_list_id": None,
        "description": None,
        "completed": None,
    }

    actual = uut.TodoUpdate(**todo_dict)

    assert actual.dict() == expected


def test_TodoUpdate():
    todo_dict = {
        "todo_list_id": UUID("7eb80ffa-b954-4c57-8fdf-5bc66fdc31de"),
        "description": "wash dogs",
        "completed": False,
    }

    expected = todo_dict

    actual = uut.TodoUpdate(**todo_dict)

    assert actual.dict() == expected


def test_TodoDb_optional_fields(todo_dict):
    todo_dict.pop("date_modified")

    expected = todo_dict
    expected["id"] = None
    expected["date_modified"] = None

    actual = uut.TodoDb(**todo_dict)

    assert actual.dict() == expected


def test_TodoDb(todo_dict):
    todo_dict["date_modified"] = datetime(2020, 1, 1, 0, 0)

    expected = todo_dict
    expected["id"] = None

    actual = uut.TodoDb(**todo_dict)

    assert actual.dict() == expected
