import os

from ariadne import load_schema_from_path

from app.core import logger as trace
from app.core.logger import get_logger
from app.ext.api.graphql_utils import get_populated_object_type, secure_graphql
from app.ext.todos.crud import create_todo, get_todos, remove_todo, update_todo
from app.ext.todos.models import (
    Todo,
    TodoCreate,
    TodoResponse,
    TodosResponse,
    TodoUpdate,
)

logger = get_logger(__name__)

types = [
    get_populated_object_type(Todo),
    get_populated_object_type(TodosResponse),
    get_populated_object_type(TodoResponse),
]

type_defs = load_schema_from_path(os.path.dirname(__file__))


@trace.debug(logger)
def populate_query(query):
    @query.field("get_todos")
    async def resolve_get_todos(_, info, todo_list=None, incomplete_only=None):
        secure = await secure_graphql(info, TodosResponse)
        if secure.error:
            return secure.error
        result = await get_todos(
            username=secure.user.username,
            todo_list=todo_list,
            incomplete_only=incomplete_only,
        )
        return TodosResponse(todos=result)


@trace.debug(logger)
def populate_mutation(mutation):
    @mutation.field("create_todo")
    async def resolve_create_todo(_, info, input):
        logger.debug(f"input: {input}")
        secure = await secure_graphql(info, TodoResponse)
        if secure.error:
            return secure.error
        result = await create_todo(
            username=secure.user.username, todo_create=TodoCreate(**input)
        )
        return TodoResponse(todo=result)

    @mutation.field("update_todo")
    async def resolve_update_todo(_, info, input):
        logger.debug(f"input: {input}")
        secure = await secure_graphql(info, TodoResponse)
        if secure.error:
            return secure.error
        result = await update_todo(
            username=secure.user.username, todo_update=TodoUpdate(**input)
        )
        if result:
            response = TodoResponse(todo=result)
        else:
            response = TodoResponse(errors=["Todo not found"])
        return response

    @mutation.field("remove_todo")
    async def resolve_remove_todo(_, info, todo_id: str):
        logger.debug(f"todo_id: {todo_id}")
        secure = await secure_graphql(info, TodoResponse)
        if secure.error:
            return secure.error
        result = await remove_todo(username=secure.user.username, todo_id=todo_id)
        response = None
        if result:
            response = TodoResponse(todo=result)
        else:
            response = TodoResponse(errors=["Todo not found"])
        return response
