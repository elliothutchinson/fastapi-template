from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, constr

TODO_DOC_TYPE = "todo"


class Todo(BaseModel):
    todo_id: str
    todo_list: str
    description: str
    completed: bool = False
    date_created: datetime
    date_modified: datetime = None


class TodoCreate(BaseModel):
    todo_list: constr(min_length=1)
    description: constr(min_length=1)


class TodoUpdate(BaseModel):
    todo_id: str
    todo_list: Optional[constr(min_length=1)]
    description: Optional[constr(min_length=1)]
    completed: Optional[bool]


class TodoUpdateDb(BaseModel):
    todo_list: Optional[str]
    description: Optional[constr(min_length=1)]
    completed: Optional[bool]
    date_modified: Optional[datetime]


class TodosResponse(BaseModel):
    todos: List[Todo] = []
    errors: List[str] = []


class TodoResponse(BaseModel):
    todo: Todo = None
    errors: List[str] = []


class TodoDb(Todo):
    type: str = TODO_DOC_TYPE
    username: constr(min_length=1)
