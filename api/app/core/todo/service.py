from datetime import datetime
from typing import List
from uuid import UUID

from pymongo.errors import DuplicateKeyError

from app.core.exception import DataConflictException, ResourceNotFoundException
from app.core.logging import get_logger

from .model import (
    TodoCreate,
    TodoDb,
    TodoListCreate,
    TodoListDb,
    TodoListUpdate,
    TodoUpdate,
)

logger = get_logger(__name__)


async def create_todo_list(
    username: str, todo_list_create: TodoListCreate
) -> TodoListDb:
    todo_list_db = TodoListDb(
        **todo_list_create.dict(), username=username, date_created=datetime.now()
    )

    try:
        await todo_list_db.insert()
    except DuplicateKeyError as dke:
        logger.error(dke)
        raise DataConflictException(
            f"Todo list resource already exists with id '{todo_list_create.todo_list_id}'"  # pylint: disable=line-too-long
        ) from dke

    return todo_list_db


async def fetch_todo_lists(username: str) -> List[TodoListDb]:
    todo_list_dbs = await TodoListDb.find_many(
        TodoListDb.username == username
    ).to_list()

    return todo_list_dbs


async def update_todo_list(
    username: str, todo_list_id: UUID, todo_list_update: TodoListUpdate
) -> TodoListDb:
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

    todo_list_db.date_modified = datetime.now()

    await todo_list_db.replace()

    return todo_list_db


async def delete_todo_list(username: str, todo_list_id: UUID) -> TodoListDb:
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

    return todo_list_db


async def validate_todo_list(username: str, todo_list_id: UUID):
    todo_list_dbs = (
        await TodoListDb.find(TodoListDb.todo_list_id == todo_list_id)
        .find(TodoListDb.username == username)
        .to_list()
    )

    todo_list_db = None
    if todo_list_dbs:
        todo_list_db = todo_list_dbs[0]

    if not todo_list_db:
        raise DataConflictException(
            f"Todo list resource not found with id '{todo_list_id}'"
        )

    return True


async def create_todo(username: str, todo_create: TodoCreate) -> TodoDb:
    await validate_todo_list(username=username, todo_list_id=todo_create.todo_list_id)

    todo_db = TodoDb(
        **todo_create.dict(), username=username, date_created=datetime.now()
    )

    try:
        await todo_db.insert()
    except DuplicateKeyError as dke:
        logger.error(dke)
        raise DataConflictException(
            f"Todo resource already exists with id '{todo_create.todo_id}'"
        ) from dke

    return todo_db


async def fetch_todos(
    username: str, todo_list_id: UUID = None, incomplete_only: bool = False
) -> List[TodoDb]:
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

    return todo_dbs


async def update_todo(username: str, todo_id: UUID, todo_update: TodoUpdate) -> TodoDb:
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
        await validate_todo_list(
            username=username, todo_list_id=todo_update.todo_list_id
        )
        todo_db.todo_list_id = todo_update.todo_list_id

    if todo_update.description:
        todo_db.description = todo_update.description

    if todo_update.completed:
        todo_db.completed = todo_update.completed

    todo_db.date_modified = datetime.now()

    await todo_db.replace()

    return todo_db


async def delete_todo(username: str, todo_id: UUID) -> TodoDb:
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

    return todo_db
