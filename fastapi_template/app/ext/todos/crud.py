import uuid
from datetime import datetime

from app.core import logger as trace
from app.core.db.crud_utils import get_doc, insert, remove, run_query, update
from app.core.db.db_utils import get_db_context
from app.core.db.models import DbContext
from app.core.logger import get_logger
from app.ext.todos.models import (
    TODO_DOC_TYPE,
    TodoCreate,
    TodoDb,
    TodoUpdate,
    TodoUpdateDb,
)

logger = get_logger(__name__)


@trace.debug(logger)
def get_todo_doc_id(username: str, todo_id: str):
    return f"{TODO_DOC_TYPE}::{username}::{todo_id}"


@trace.debug(logger)
async def get_todos(
    username: str, todo_list: str = None, incomplete_only: bool = False
):
    db_context = await get_db_context()
    where_clause = "doc->>'username'=$1"
    where_values = [username]
    if todo_list:
        where_clause += " and doc->>'todo_list'=$2"
        where_values.append(todo_list)
    if incomplete_only:
        where_clause += " and doc->>'date_completed' is null"
    todos = await run_query(
        db_context=db_context,
        doc_type=TODO_DOC_TYPE,
        doc_model=TodoDb,
        where_clause=where_clause,
        where_values=where_values,
        order_by="doc->>'date_created' desc",
        limit=1000,
    )
    return todos


@trace.debug(logger)
async def get_todo_from_db(db_context: DbContext, doc_id: str):
    return await get_doc(db_context=db_context, doc_id=doc_id, doc_model=TodoDb)


@trace.debug(logger)
async def create_todo(username: str, todo_create: TodoCreate):
    todo_id = str(uuid.uuid4())
    doc_id = get_todo_doc_id(username=username, todo_id=todo_id)
    todo_db = TodoDb(
        **todo_create.dict(),
        username=username,
        todo_id=todo_id,
        date_created=datetime.now(),
    )
    db_context = await get_db_context()
    return await insert(db_context=db_context, doc_id=doc_id, doc_in=todo_db)


@trace.debug(logger)
async def update_todo(username: str, todo_update: TodoUpdate):
    doc_id = get_todo_doc_id(username=username, todo_id=todo_update.todo_id)
    db_context = await get_db_context()
    todo = await get_todo_from_db(db_context=db_context, doc_id=doc_id)
    if not todo:
        return None
    todo_update_db = TodoUpdateDb(date_modified=datetime.now(), **todo_update.dict())
    return await update(
        db_context=db_context, doc_id=doc_id, doc=todo, doc_updated=todo_update_db
    )


@trace.debug(logger)
async def remove_todo(username: str, todo_id: str):
    doc_id = get_todo_doc_id(username=username, todo_id=todo_id)
    db_context = await get_db_context()
    return await remove(db_context=db_context, doc_id=doc_id, doc_model=TodoDb)
