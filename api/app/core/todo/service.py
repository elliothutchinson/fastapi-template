# todo: implement
from typing import List
from .model import TodoDb, Todo


"""
paging support
complete/incomplete filter
list filter
crud todo
crud todolist
bulk update
"""


async def fetch_todos(username: str) -> List[TodoDb]:
    pass


async def create_todo(todo: Todo) -> TodoDb:
    pass


async def update_todo(id: str, todo: Todo) -> TodoDb:
    pass


async def delete_todo(id: str) -> TodoDb:
    pass
