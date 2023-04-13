from datetime import timezone

from factory import Faker, Trait

from app.core.todo.model import (
    Todo,
    TodoCreate,
    TodoList,
    TodoListCreate,
    TodoListUpdate,
    TodoUpdate,
)
from app.core.todo.repo import TodoDb, TodoListDb

from .base_factory import BaseDbFactory, BaseFactory


class TodoListFactory(BaseFactory):
    todo_list_id = Faker("uuid4")
    list_name = Faker("pystr")
    date_created = Faker("date_time", tzinfo=timezone.utc)
    date_modified = Faker("date_time", tzinfo=timezone.utc)

    class Meta:
        model = TodoList

    class Params:
        created = Trait(
            date_modified=None,
        )


class TodoListDbFactory(TodoListFactory, BaseDbFactory):
    username = Faker("pystr")

    class Meta:
        model = TodoListDb


class TodoListUpdateFactory(BaseFactory):
    list_name = Faker("pystr")

    class Meta:
        model = TodoListUpdate


class TodoListCreateFactory(TodoListUpdateFactory):
    todo_list_id = Faker("uuid4")

    class Meta:
        model = TodoListCreate


class TodoFactory(BaseFactory):
    todo_id = Faker("uuid4")
    todo_list_id = Faker("uuid4")
    description = Faker("pystr")
    completed = Faker("pybool")
    date_created = Faker("date_time", tzinfo=timezone.utc)
    date_modified = Faker("date_time", tzinfo=timezone.utc)

    class Meta:
        model = Todo

    class Params:
        created = Trait(
            date_modified=None,
            completed=False,
        )


class TodoDbFactory(TodoFactory, BaseDbFactory):
    username = Faker("pystr")

    class Meta:
        model = TodoDb


class TodoUpdateFactory(BaseFactory):
    todo_list_id = Faker("uuid4")
    description = Faker("pystr")
    completed = Faker("pybool")

    class Meta:
        model = TodoUpdate


class TodoCreateFactory(TodoUpdateFactory):
    todo_id = Faker("uuid4")

    class Meta:
        model = TodoCreate
