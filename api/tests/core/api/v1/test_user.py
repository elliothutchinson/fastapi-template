from datetime import datetime
from unittest.mock import Mock, patch

import orjson
import pytest


@patch(
    "app.core.user.service.datetime",
    Mock(now=Mock(return_value=datetime(2020, 1, 1, 0, 0))),
)
def test_register_new_user(client, _setup_db, user_create, user):
    expected = user.dict()
    expected["verified_email"] = None
    expected["date_modified"] = None
    expected["last_login"] = None
    expected_json = orjson.dumps(expected).decode()
    expected_json_dict = orjson.loads(expected_json)

    user_create_dict = user_create.dict()
    user_create_dict["password"] = user_create.password.get_secret_value()
    user_create_dict["password_match"] = user_create.password.get_secret_value()

    actual = client.post("/api/v1/user/", json=user_create_dict)
    actual_json = actual.json()

    assert actual.status_code == 200
    assert actual_json == expected_json_dict


@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
def test_read_current_user(client, _setup_db_user_db, _setup_cache, user, auth_headers):
    expected = user.dict()
    expected_json = orjson.dumps(expected).decode()
    expected_json_dict = orjson.loads(expected_json)

    actual = client.get("/api/v1/user/", headers=auth_headers)
    actual_json = actual.json()

    assert actual.status_code == 200
    assert actual_json == expected_json_dict


@patch(
    "app.core.user.service.datetime",
    Mock(now=Mock(return_value=datetime(2020, 1, 5, 0, 0))),
)
@patch("jwt.api_jwt._jwt_global_obj._validate_exp", Mock(return_value=None))
def test_update_current_user(
    client, _setup_db_user_db, _setup_cache, user_update, user_db, auth_headers
):
    user_update_dict = user_update.dict()
    user_update_dict["password"] = user_update.password.get_secret_value()
    user_update_dict["password_match"] = user_update.password.get_secret_value()

    expected = user_db.dict()
    expected.update(user_update_dict)
    expected["date_modified"] = datetime(2020, 1, 5, 0, 0)
    expected.pop("id")
    expected.pop("password")
    expected.pop("password_match")
    expected.pop("password_hash")
    expected_json = orjson.dumps(expected).decode()
    expected_json_dict = orjson.loads(expected_json)

    actual = client.put("/api/v1/user/", json=user_update_dict, headers=auth_headers)
    actual_json = actual.json()

    assert actual.status_code == 200
    assert actual_json == expected_json_dict
