from locust import task

from tests.factories.server_response_factory import ServerResponseFactory
from tests.perf.util import ApiUser


class HealthApiUser(ApiUser):
    @task
    def health(self):
        expected = ServerResponseFactory.build(message="OK").dict()

        with self.rest("GET", "/api/v1/health") as response:
            actual = response.js
            self.validate(actual, expected)
