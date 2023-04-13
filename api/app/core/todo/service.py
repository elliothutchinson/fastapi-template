from uuid import UUID

from app.core.logging import get_logger
from app.core.todo import repo as todo_repo

from .model import (
    Todo,
    TodoCreate,
    TodoList,
    TodoListCreate,
    TodoListUpdate,
    TodoUpdate,
)

logger = get_logger(__name__)


async def create_todo_list(username: str, todo_list_create: TodoListCreate) -> TodoList:
    return await todo_repo.create_todo_list(
        username=username, todo_list_create=todo_list_create
    )


async def fetch_todo_lists(username: str) -> list[TodoList]:
    return await todo_repo.fetch_todo_lists(username)


async def update_todo_list(
    username: str, todo_list_id: UUID, todo_list_update: TodoListUpdate
) -> TodoList:
    return await todo_repo.update_todo_list(
        username=username, todo_list_id=todo_list_id, todo_list_update=todo_list_update
    )


async def delete_todo_list(username: str, todo_list_id: UUID) -> TodoList:
    return await todo_repo.delete_todo_list(
        username=username, todo_list_id=todo_list_id
    )


async def create_todo(username: str, todo_create: TodoCreate) -> Todo:
    return await todo_repo.create_todo(username=username, todo_create=todo_create)


async def fetch_todos(
    username: str, todo_list_id: UUID = None, incomplete_only: bool = False
) -> list[Todo]:
    return await todo_repo.fetch_todos(
        username=username, todo_list_id=todo_list_id, incomplete_only=incomplete_only
    )


async def update_todo(username: str, todo_id: UUID, todo_update: TodoUpdate) -> Todo:
    return await todo_repo.update_todo(
        username=username, todo_id=todo_id, todo_update=todo_update
    )


async def delete_todo(username: str, todo_id: UUID) -> Todo:
    return await todo_repo.delete_todo(username=username, todo_id=todo_id)
