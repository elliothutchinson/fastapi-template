from locust import task

from tests import util
from tests.factories.todo_factory import (
    TodoCreateFactory,
    TodoFactory,
    TodoListCreateFactory,
    TodoListFactory,
    TodoListUpdateFactory,
    TodoUpdateFactory,
)
from tests.perf.util import ApiUser


class TodoApiUser(ApiUser):
    @task
    def create_todo_list(self):
        created_todo_list = None
        self.pre_task()

        todo_list_create = TodoListCreateFactory.build()
        todo_list_create_json_dict = util.json_dict(todo_list_create.dict())

        expected = util.json_dict(
            TodoListFactory.build(created=True, **todo_list_create.dict()).dict(
                exclude={"date_created"}
            )
        )

        with self.rest(
            "POST",
            "/api/v1/todo/list",
            headers=self.headers,
            json=todo_list_create_json_dict,
        ) as response:
            if response.status_code == 200:
                actual = response.js
                actual.pop("date_created")
                self.validate(actual, expected)
                created_todo_list = actual

        return created_todo_list

    @task
    def fetch_todo_lists(self):
        self.pre_task()

        expected = list(TodoListFactory.build().dict())

        with self.rest("GET", "/api/v1/todo/list", headers=self.headers) as response:
            if response.status_code == 200:
                todo_lists = response.js
                if todo_lists:
                    actual = list(todo_lists[0])
                    self.validate(actual, expected)

    @task
    def update_todo_list(self):
        self.pre_task()

        todo_list_dict = self.create_todo_list()
        assert todo_list_dict is not None

        todo_list_update = TodoListUpdateFactory.build()
        todo_list_update_json_dict = util.json_dict(todo_list_update.dict())

        updated_todo_list_dict = todo_list_dict | todo_list_update.dict()

        expected = util.json_dict(
            TodoListFactory.build(
                **updated_todo_list_dict,
            ).dict(exclude={"date_created", "date_modified"})
        )

        with self.rest(
            "PUT",
            f"/api/v1/todo/list/{todo_list_dict['todo_list_id']}",
            headers=self.headers,
            json=todo_list_update_json_dict,
            name="/api/v1/todo/list/{todo_list_id}",
        ) as response:
            if response.status_code == 200:
                actual = response.js
                actual.pop("date_created")
                actual.pop("date_modified")
                self.validate(actual, expected)

    @task
    def delete_todo_list(self):
        self.pre_task()

        todo_list_dict = self.create_todo_list()
        assert todo_list_dict is not None

        expected = todo_list_dict

        with self.rest(
            "DELETE",
            f"/api/v1/todo/list/{todo_list_dict['todo_list_id']}",
            headers=self.headers,
            name="/api/v1/todo/list/{todo_list_id}",
        ) as response:
            if response.status_code == 200:
                actual = response.js
                actual.pop("date_created")
                self.validate(actual, expected)

    @task
    def create_todo(self):
        created_todo = None
        self.pre_task()

        todo_list_dict = self.create_todo_list()
        assert todo_list_dict is not None

        todo_create = TodoCreateFactory.build(
            todo_list_id=todo_list_dict["todo_list_id"]
        )
        todo_create_json_dict = util.json_dict(todo_create.dict())

        expected = util.json_dict(
            TodoFactory.build(created=True, **todo_create.dict()).dict(
                exclude={"date_created"}
            )
        )

        with self.rest(
            "POST",
            "/api/v1/todo/task",
            headers=self.headers,
            json=todo_create_json_dict,
        ) as response:
            if response.status_code == 200:
                actual = response.js
                actual.pop("date_created")
                self.validate(actual, expected)
                created_todo = actual

        return created_todo

    @task
    def fetch_todos(self):
        self.pre_task()

        expected = list(TodoFactory.build().dict())

        with self.rest("GET", "/api/v1/todo/task", headers=self.headers) as response:
            if response.status_code == 200:
                todos = response.js
                if todos:
                    actual = list(todos[0])
                    self.validate(actual, expected)

    @task
    def update_todo(self):
        self.pre_task()

        todo_dict = self.create_todo()
        assert todo_dict is not None

        todo_list_dict = self.create_todo_list()
        assert todo_list_dict is not None

        todo_update = TodoUpdateFactory.build(
            todo_list_id=todo_list_dict["todo_list_id"]
        )
        todo_update_json_dict = util.json_dict(todo_update.dict())

        updated_todo_dict = todo_dict | todo_update.dict()

        expected = util.json_dict(
            TodoFactory.build(
                **updated_todo_dict,
            ).dict(exclude={"date_created", "date_modified"})
        )

        with self.rest(
            "PUT",
            f"/api/v1/todo/task/{todo_dict['todo_id']}",
            headers=self.headers,
            json=todo_update_json_dict,
            name="/api/v1/todo/task/{todo_id}",
        ) as response:
            if response.status_code == 200:
                actual = response.js
                actual.pop("date_created")
                actual.pop("date_modified")
                self.validate(actual, expected)

    @task
    def delete_todo(self):
        self.pre_task()

        todo_dict = self.create_todo()
        assert todo_dict is not None

        expected = todo_dict

        with self.rest(
            "DELETE",
            f"/api/v1/todo/task/{todo_dict['todo_id']}",
            headers=self.headers,
            name="/api/v1/todo/task/{todo_id}",
        ) as response:
            if response.status_code == 200:
                actual = response.js
                actual.pop("date_created")
                self.validate(actual, expected)
