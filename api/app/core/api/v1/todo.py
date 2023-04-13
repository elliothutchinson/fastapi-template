from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.security.auth import get_user_from_token
from app.core.todo import service as todo_service
from app.core.todo.model import (
    Todo,
    TodoCreate,
    TodoList,
    TodoListCreate,
    TodoListUpdate,
    TodoUpdate,
)
from app.core.user.model import UserPublic

router = APIRouter()


@router.post("/list", response_model=TodoList)
async def create_todo_list(
    todo_list_create: TodoListCreate,
    current_user: UserPublic = Depends(get_user_from_token),
):
    todo_list = await todo_service.create_todo_list(
        username=current_user.username, todo_list_create=todo_list_create
    )

    return todo_list


@router.get("/list", response_model=list[TodoList])
async def fetch_todo_lists(
    current_user: UserPublic = Depends(get_user_from_token),
):
    todo_lists = await todo_service.fetch_todo_lists(current_user.username)

    return todo_lists


@router.put("/list/{todo_list_id}", response_model=TodoList)
async def update_todo_list(
    todo_list_id: UUID,
    todo_list_update: TodoListUpdate,
    current_user: UserPublic = Depends(get_user_from_token),
):
    todo_list = await todo_service.update_todo_list(
        username=current_user.username,
        todo_list_id=todo_list_id,
        todo_list_update=todo_list_update,
    )

    return todo_list


@router.delete("/list/{todo_list_id}", response_model=TodoList)
async def delete_todo_list(
    todo_list_id: UUID,
    current_user: UserPublic = Depends(get_user_from_token),
):
    todo_list = await todo_service.delete_todo_list(
        username=current_user.username, todo_list_id=todo_list_id
    )

    return todo_list


@router.post("/task", response_model=Todo)
async def create_todo(
    todo_create: TodoCreate,
    current_user: UserPublic = Depends(get_user_from_token),
):
    todo = await todo_service.create_todo(
        username=current_user.username, todo_create=todo_create
    )

    return todo


@router.get("/task", response_model=list[Todo])
async def fetch_todos(
    todo_list_id: UUID = None,
    incomplete_only: bool = False,
    current_user: UserPublic = Depends(get_user_from_token),
):
    todos = await todo_service.fetch_todos(
        username=current_user.username,
        todo_list_id=todo_list_id,
        incomplete_only=incomplete_only,
    )

    return todos


@router.put("/task/{todo_id}", response_model=Todo)
async def update_todo(
    todo_id: UUID,
    todo_update: TodoUpdate,
    current_user: UserPublic = Depends(get_user_from_token),
):
    todo = await todo_service.update_todo(
        username=current_user.username, todo_id=todo_id, todo_update=todo_update
    )

    return todo


@router.delete("/task/{todo_id}", response_model=Todo)
async def delete_todo(
    todo_id: UUID,
    current_user: UserPublic = Depends(get_user_from_token),
):
    todo = await todo_service.delete_todo(
        username=current_user.username, todo_id=todo_id
    )

    return todo
