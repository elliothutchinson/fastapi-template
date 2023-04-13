from datetime import datetime, timedelta, timezone

from locust import FastHttpUser

from tests import util
from tests.factories.token_factory import AuthTokenFactory
from tests.factories.user_factory import UserCreateFactory, UserPublicFactory


class ApiUser(FastHttpUser):
    abstract = True

    def __init__(self, env):
        super().__init__(env)
        self.created_user = None
        self.auth_token = None
        self.headers = None

    def register(self):
        registered_user = None
        user_create = UserCreateFactory.build()
        user_create_json_dict = util.json_dict(user_create.dict())

        expected = util.json_dict(
            UserPublicFactory.build(
                **user_create.dict(),
                date_modified=None,
                last_login=None,
            ).dict(exclude={"date_created"})
        )

        with self.rest("POST", "/api/v1/user", json=user_create_json_dict) as response:
            if response.status_code == 200:
                actual = response.js
                actual.pop("date_created")
                self.validate(actual, expected)
                registered_user = user_create

        return registered_user

    def create_user(self):
        user_create = self.register()
        self.created_user = user_create

    def login(self):
        auth_token = None
        credential = {
            "username": self.created_user.username,
            "password": self.created_user.password.get_secret_value(),
        }
        expected = list(AuthTokenFactory.build().dict())

        with self.client.post("/api/v1/auth/login", data=credential) as response:
            if response.status_code == 200:
                token = response.json()
                actual = list(token)
                self.validate(actual, expected)
                auth_token = token

        return auth_token

    def login_user(self):
        auth_token = self.login()
        self.auth_token = AuthTokenFactory.build(**auth_token)
        self.headers = util.authorization_header(self.auth_token.access_token)

    def refresh(self):
        auth_token = None

        auth_token_json_dict = util.json_dict(self.auth_token.dict())

        expected = list(AuthTokenFactory.build().dict())

        with self.rest(
            "POST", "/api/v1/auth/refresh", json=auth_token_json_dict
        ) as response:
            if response.status_code == 200:
                token = response.json()
                actual = list(token)
                self.validate(actual, expected)
                auth_token = token
        return auth_token

    def refresh_token(self):
        auth_token = self.refresh()
        self.auth_token = AuthTokenFactory.build(**auth_token)
        self.headers = util.authorization_header(self.auth_token.access_token)

    def pre_task(self):
        if not self.created_user:
            self.create_user()

        if not self.auth_token:
            self.login_user()

        if self.auth_token.refresh_token_expires_at < datetime.now(
            timezone.utc
        ) - timedelta(seconds=5):
            self.login_user()

        if self.auth_token.access_token_expires_at < datetime.now(
            timezone.utc
        ) - timedelta(seconds=5):
            self.refresh_token()

    def validate(self, actual, expected):
        assert actual == expected, f"{actual} != {expected}"
