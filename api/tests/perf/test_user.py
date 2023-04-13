from locust import task

from tests import util
from tests.factories.user_factory import UserPublicFactory, UserUpdateFactory
from tests.perf.util import ApiUser


class UserApiUser(ApiUser):
    @task
    def register_new_user(self):
        self.register()

    @task
    def read_current_user(self):
        self.pre_task()

        expected = util.json_dict(
            UserPublicFactory.build(
                **self.created_user.dict(),
            ).dict(exclude={"date_created", "date_modified", "last_login"})
        )

        with self.rest("GET", "/api/v1/user", headers=self.headers) as response:
            if response.status_code == 200:
                actual = response.js
                actual.pop("date_created")
                actual.pop("date_modified")
                actual.pop("last_login")
                self.validate(actual, expected)

    @task
    def update_curent_user(self):
        # pylint: disable=duplicate-code
        self.pre_task()

        user_update = UserUpdateFactory.build()
        user_update_json_dict = util.json_dict(user_update.dict())
        updated_user = self.created_user.copy(update=user_update.dict())

        expected = util.json_dict(
            UserPublicFactory.build(
                **updated_user.dict(),
            ).dict(exclude={"date_created", "date_modified", "last_login"})
        )

        with self.rest(
            "PUT", "/api/v1/user", headers=self.headers, json=user_update_json_dict
        ) as response:
            if response.status_code == 200:
                actual = response.js
                actual.pop("date_created")
                actual.pop("date_modified")
                actual.pop("last_login")
                self.validate(actual, expected)
                self.created_user = updated_user
