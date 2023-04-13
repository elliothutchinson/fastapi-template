from locust import task

from tests import util
from tests.factories.server_response_factory import ServerResponseFactory
from tests.perf.util import ApiUser


class AuthApiUser(ApiUser):
    @task
    def login_for_auth_token(self):
        self.pre_task()
        self.login()

    @task
    def logout_auth_token(self):
        self.pre_task()

        auth_token_json_dict = util.json_dict(self.auth_token.dict())

        expected = ServerResponseFactory.build(
            message="access_token revoked: True, refresh_token revoked: True"
        )

        with self.rest(
            "POST",
            "/api/v1/auth/logout",
            headers=self.headers,
            json=auth_token_json_dict,
        ) as response:
            if response.status_code == 200:
                actual = response.js
                self.validate(actual, expected)
                self.auth_token = None
                self.headers = None

    @task
    def refresh_auth_token(self):
        self.pre_task()
        self.refresh()
