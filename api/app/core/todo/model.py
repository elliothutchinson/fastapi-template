from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TodoList(BaseModel):
    todo_list_id: UUID
    list_name: str
    date_created: datetime
    date_modified: datetime | None = None


class TodoListCreate(BaseModel):
    todo_list_id: UUID
    list_name: str


class TodoListUpdate(BaseModel):
    list_name: Optional[str]


class Todo(BaseModel):
    todo_id: UUID
    todo_list_id: UUID
    description: str
    completed: bool
    date_created: datetime
    date_modified: datetime | None = None


class TodoCreate(BaseModel):
    todo_id: UUID
    todo_list_id: UUID
    description: str
    completed: bool


class TodoUpdate(BaseModel):
    todo_list_id: Optional[UUID]
    description: Optional[str]
    completed: Optional[bool]
