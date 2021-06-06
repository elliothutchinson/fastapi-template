import uuid

from app.core.config import core_config

PASSWORD = "password"
TEST_USER_PREFIX = "testuser"
TEST_EMAIL_SUFFIX = "@test.com"


def get_test_username():
    return f"{TEST_USER_PREFIX}{uuid.uuid4()}"


def register_user(client, username, email=None):
    if not email:
        email = f"{username}{TEST_EMAIL_SUFFIX}"
    response = client.post(
        f"{core_config.get_current_api()}/users/",
        json={
            "username": username,
            "full_name": "test user",
            "email": email,
            "password": PASSWORD,
            "disabled": False,
        },
    )
    return response


def get_access_token(client, username, password):
    response = client.post(
        f"{core_config.get_current_api()}{core_config.login_path}{core_config.token_path}",
        data={"username": username, "password": password},
    )
    token = response.json()
    return token, response
