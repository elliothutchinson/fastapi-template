from datetime import datetime
from typing import Optional
from uuid import UUID

from beanie import Document, Indexed
from pydantic import BaseModel


class TodoList(BaseModel):
    todo_list_id: UUID
    list_name: str


class TodoListCreate(BaseModel):
    todo_list_id: UUID
    list_name: str


class TodoListUpdate(BaseModel):
    list_name: Optional[str]


class TodoListDb(Document):
    todo_list_id: Indexed(UUID, unique=True)
    list_name: str
    username: str
    date_created: datetime
    date_modified: datetime | None = None


class Todo(BaseModel):
    todo_id: UUID
    todo_list_id: UUID
    description: str
    completed: bool


class TodoCreate(BaseModel):
    todo_id: UUID
    todo_list_id: UUID
    description: str
    completed: bool


class TodoUpdate(BaseModel):
    todo_list_id: Optional[UUID]
    description: Optional[str]
    completed: Optional[bool]


class TodoDb(Document):
    todo_id: Indexed(UUID, unique=True)
    todo_list_id: UUID
    description: str
    completed: bool
    username: str
    date_created: datetime
    date_modified: datetime | None = None
