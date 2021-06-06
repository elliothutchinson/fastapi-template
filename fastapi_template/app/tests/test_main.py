import asyncio
import time

from starlette.testclient import TestClient

from app.core.config import core_config
from app.main import app
from app.tests.db_utils import clean_up_db
from app.tests.utils import (
    PASSWORD,
    TEST_EMAIL_SUFFIX,
    get_access_token,
    get_test_username,
    register_user,
)

client = TestClient(app)


def teardown_module():
    time.sleep(3)  # wait for query service / eventual consistency
    asyncio.get_event_loop().run_until_complete(clean_up_db())


def test_register_user():
    username = get_test_username()
    response = register_user(client, username)
    assert response.status_code == 200
    different_email = f"{get_test_username()}{TEST_EMAIL_SUFFIX}"
    response = register_user(client, username, email=different_email)
    assert response.json() == {"detail": "Resource already exists"}
    assert response.status_code == 409
    different_username = get_test_username()
    response = register_user(
        client, different_username, email=f"{username}{TEST_EMAIL_SUFFIX}"
    )
    assert response.json() == {"detail": "An account already exists with this email"}
    assert response.status_code == 409


def test_read_user():
    username = get_test_username()
    response = register_user(client, username)
    assert response.status_code == 200
    response = client.get(f"{core_config.get_current_api()}/users/username/{username}")
    assert response.status_code == 200
    assert response.json() == {
        "username": username,
        "full_name": "test user",
    }


def test_read_user_nonexistent():
    username = get_test_username()
    response = client.get(f"{core_config.get_current_api()}/users/username/{username}")
    assert response.status_code == 404


def test_read_user_by_email():
    username = get_test_username()
    response = register_user(client, username)
    assert response.status_code == 200
    time.sleep(3)  # wait for query service / eventual consistency
    response = client.get(
        f"{core_config.get_current_api()}/users/email/{username}{TEST_EMAIL_SUFFIX}"
    )
    assert response.status_code == 200
    assert response.json() == {
        "username": username,
        "full_name": "test user",
    }


def test_read_user_by_email_nonexistent():
    username = get_test_username()
    response = client.get(
        f"{core_config.get_current_api()}/users/email/{username}{TEST_EMAIL_SUFFIX}"
    )
    assert response.status_code == 404


def test_login_access_token():
    username = get_test_username()
    response = register_user(client, username)
    assert response.status_code == 200
    token, response = get_access_token(client, username, PASSWORD)
    assert response.status_code == 200
    assert "token_type" in token
    assert "access_token" in token


def test_login_access_token_invalid_username():
    username = get_test_username()
    token, response = get_access_token(client, username, PASSWORD)
    assert response.status_code == 401
    assert token == {"detail": "Invalid credentials"}


def test_login_access_token_invalid_password():
    username = get_test_username()
    response = register_user(client, username)
    assert response.status_code == 200
    token, response = get_access_token(client, username, "invalid")
    assert response.status_code == 401
    assert token == {"detail": "Invalid credentials"}


def test_read_current_user():
    username = get_test_username()
    response = register_user(client, username)
    assert response.status_code == 200
    token, response = get_access_token(client, username, PASSWORD)
    assert response.status_code == 200
    assert "token_type" in token
    assert "access_token" in token
    response = client.get(
        f"{core_config.get_current_api()}/users/",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    assert response.status_code == 200
    json = response.json()
    assert json["date_created"] is not None
    assert json["last_login"] is not None
    new_json = {k: json[k] for k in json.keys() - {"date_created", "last_login"}}
    assert new_json == {
        "username": username,
        "full_name": "test user",
        "email": f"{username}{TEST_EMAIL_SUFFIX}",
        "disabled": False,
        "verified": False,
        "date_modified": None,
    }


def test_read_current_user_no_token():
    username = get_test_username()
    response = register_user(client, username)
    assert response.status_code == 200
    response = client.get(f"{core_config.get_current_api()}/users/")
    assert response.status_code == 401


def test_update_user():
    another_username = get_test_username()
    response = register_user(client, another_username)
    assert response.status_code == 200
    username = get_test_username()
    response = register_user(client, username)
    assert response.status_code == 200
    token, response = get_access_token(client, username, PASSWORD)
    assert response.status_code == 200
    assert "token_type" in token
    assert "access_token" in token
    changed_email = f"{get_test_username()}{TEST_EMAIL_SUFFIX}"
    response = client.put(
        f"{core_config.get_current_api()}/users/",
        headers={"Authorization": f"Bearer {token['access_token']}"},
        json={
            "full_name": "changedtest user",
            "email": changed_email,
            "password": "changed",
        },
    )
    assert response.status_code == 200
    response = client.get(
        f"{core_config.get_current_api()}/users/",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    assert response.status_code == 200
    json = response.json()
    assert json["date_created"] is not None
    assert json["date_modified"] is not None
    assert json["last_login"] is not None
    new_json = {
        k: json[k]
        for k in json.keys() - {"date_created", "date_modified", "last_login"}
    }
    assert new_json == {
        "username": username,
        "full_name": "changedtest user",
        "email": changed_email,
        "disabled": False,
        "verified": False,
    }
    token, response = get_access_token(client, username, "changed")
    assert response.status_code == 200
    assert "token_type" in token
    assert "access_token" in token
    response = client.put(
        f"{core_config.get_current_api()}/users/",
        headers={"Authorization": f"Bearer {token['access_token']}"},
        json={"email": f"{another_username}{TEST_EMAIL_SUFFIX}"},
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "An account already exists with this email"}


def test_update_user_no_token():
    username = get_test_username()
    response = register_user(client, username)
    assert response.status_code == 200
    response = client.put(
        f"{core_config.get_current_api()}/users/",
        json={
            "full_name": "changedtest user",
            "email": f"changedtestuser{TEST_EMAIL_SUFFIX}",
            "password": "changed",
        },
    )
    assert response.status_code == 401
