from datetime import datetime, timezone
from typing import List
from uuid import UUID

from beanie import Document, Indexed
from pymongo.errors import DuplicateKeyError

from app.core.exception import DataConflictException, ResourceNotFoundException
from app.core.logging import get_logger

from .model import (
    Todo,
    TodoCreate,
    TodoList,
    TodoListCreate,
    TodoListUpdate,
    TodoUpdate,
)

logger = get_logger(__name__)


class TodoListDb(Document):
    todo_list_id: Indexed(UUID, unique=True)
    list_name: str
    username: str
    date_created: datetime
    date_modified: datetime | None = None


class TodoDb(Document):
    todo_id: Indexed(UUID, unique=True)
    todo_list_id: UUID
    description: str
    completed: bool
    username: str
    date_created: datetime
    date_modified: datetime | None = None


async def create_todo_list(username: str, todo_list_create: TodoListCreate) -> TodoList:
    todo_list_db = TodoListDb(
        **todo_list_create.dict(),
        username=username,
        date_created=datetime.now(timezone.utc),
    )

    try:
        await todo_list_db.insert()
    except DuplicateKeyError as dke:
        logger.error(dke)
        raise DataConflictException(
            f"Todo list resource already exists with id '{todo_list_create.todo_list_id}'"  # pylint: disable=line-too-long
        ) from dke

    return TodoList(**todo_list_db.dict())


# todo: add unit test
def _update_date_timezones_todo_list(todo_list: TodoList):
    todo_list.date_created = todo_list.date_created.replace(tzinfo=timezone.utc)
    if todo_list.date_modified:
        todo_list.date_modified = todo_list.date_modified.replace(tzinfo=timezone.utc)


async def fetch_todo_lists(username: str) -> List[TodoList]:
    todo_list_dbs = await TodoListDb.find_many(
        TodoListDb.username == username
    ).to_list()

    todo_lists = [TodoList(**todo_list_db.dict()) for todo_list_db in todo_list_dbs]

    for todo_list in todo_lists:
        _update_date_timezones_todo_list(todo_list)

    return todo_lists


async def update_todo_list(
    username: str, todo_list_id: UUID, todo_list_update: TodoListUpdate
) -> TodoList:
    todo_list_dbs = (
        await TodoListDb.find(TodoListDb.todo_list_id == todo_list_id)
        .find(TodoListDb.username == username)
        .to_list()
    )

    todo_list_db = None
    if todo_list_dbs:
        todo_list_db = todo_list_dbs[0]
    if not todo_list_db:
        raise ResourceNotFoundException(
            f"Todo list resource not found with id '{todo_list_id}'"
        )

    if todo_list_update.list_name:
        todo_list_db.list_name = todo_list_update.list_name

    todo_list_db.date_modified = datetime.now(timezone.utc)

    await todo_list_db.replace()

    todo_list = TodoList(**todo_list_db.dict())
    _update_date_timezones_todo_list(todo_list)

    return todo_list


async def delete_todo_list(username: str, todo_list_id: UUID) -> TodoList:
    todo_list_dbs = (
        await TodoListDb.find(TodoListDb.todo_list_id == todo_list_id)
        .find(TodoListDb.username == username)
        .to_list()
    )

    todo_list_db = None
    if todo_list_dbs:
        todo_list_db = todo_list_dbs[0]
    if not todo_list_db:
        raise ResourceNotFoundException(
            f"Todo list resource not found with id '{todo_list_id}'"
        )

    await TodoDb.find(TodoDb.todo_list_id == todo_list_id).find(
        TodoDb.username == username
    ).delete()

    await todo_list_db.delete()

    todo_list = TodoList(**todo_list_db.dict())
    _update_date_timezones_todo_list(todo_list)

    return todo_list


async def _validate_todo_list(username: str, todo_list_id: UUID) -> TodoListDb:
    todo_list_dbs = (
        await TodoListDb.find(TodoListDb.todo_list_id == todo_list_id)
        .find(TodoListDb.username == username)
        .to_list()
    )

    if not todo_list_dbs:
        raise DataConflictException(
            f"Todo list resource not found with id '{todo_list_id}'"
        )

    todo_list_db = todo_list_dbs[0]
    _update_date_timezones_todo_list(todo_list_db)

    return todo_list_db


async def create_todo(username: str, todo_create: TodoCreate) -> Todo:
    await _validate_todo_list(username=username, todo_list_id=todo_create.todo_list_id)

    todo_db = TodoDb(
        **todo_create.dict(), username=username, date_created=datetime.now(timezone.utc)
    )

    try:
        await todo_db.insert()
    except DuplicateKeyError as dke:
        logger.error(dke)
        raise DataConflictException(
            f"Todo resource already exists with id '{todo_create.todo_id}'"
        ) from dke

    return Todo(**todo_db.dict())


# todo: add unit test, consider moving to one
def _update_date_timezones_todo(todo: Todo):
    todo.date_created = todo.date_created.replace(tzinfo=timezone.utc)
    if todo.date_modified:
        todo.date_modified = todo.date_modified.replace(tzinfo=timezone.utc)


async def fetch_todos(
    username: str, todo_list_id: UUID = None, incomplete_only: bool = False
) -> List[Todo]:
    todo_dbs = []

    if todo_list_id and incomplete_only:
        todo_dbs = (
            await TodoDb.find(TodoDb.todo_list_id == todo_list_id)
            .find(TodoDb.username == username)
            .find(TodoDb.completed == False)  # pylint: disable=singleton-comparison
            .to_list()
        )
    elif todo_list_id:
        todo_dbs = (
            await TodoDb.find(TodoDb.todo_list_id == todo_list_id)
            .find(TodoDb.username == username)
            .to_list()
        )
    elif incomplete_only:
        todo_dbs = (
            await TodoDb.find(TodoDb.username == username)
            .find(TodoDb.completed == False)  # pylint: disable=singleton-comparison
            .to_list()
        )
    else:
        todo_dbs = await TodoDb.find(TodoDb.username == username).to_list()

    todos = [Todo(**todo_db.dict()) for todo_db in todo_dbs]

    for todo in todos:
        _update_date_timezones_todo(todo)

    return todos


async def update_todo(username: str, todo_id: UUID, todo_update: TodoUpdate) -> Todo:
    todo_dbs = (
        await TodoDb.find(TodoDb.todo_id == todo_id)
        .find(TodoDb.username == username)
        .to_list()
    )

    todo_db = None
    if todo_dbs:
        todo_db = todo_dbs[0]
    if not todo_db:
        raise ResourceNotFoundException(f"Todo resource not found with id '{todo_id}'")

    if todo_update.todo_list_id:
        await _validate_todo_list(
            username=username, todo_list_id=todo_update.todo_list_id
        )
        todo_db.todo_list_id = todo_update.todo_list_id

    if todo_update.description:
        todo_db.description = todo_update.description

    if todo_update.completed is not None:
        todo_db.completed = todo_update.completed

    todo_db.date_modified = datetime.now(timezone.utc)

    await todo_db.replace()

    todo = Todo(**todo_db.dict())
    _update_date_timezones_todo(todo)

    return todo


async def delete_todo(username: str, todo_id: UUID) -> Todo:
    todo_dbs = (
        await TodoDb.find(TodoDb.todo_id == todo_id)
        .find(TodoDb.username == username)
        .to_list()
    )

    todo_db = None
    if todo_dbs:
        todo_db = todo_dbs[0]
    if not todo_db:
        raise ResourceNotFoundException(f"Todo resource not found with id '{todo_id}'")

    await todo_db.delete()

    todo = Todo(**todo_db.dict())
    _update_date_timezones_todo(todo)

    return todo
