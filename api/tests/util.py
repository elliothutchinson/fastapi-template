from datetime import datetime


def convert_to_env_vars(data: dict) -> dict:

    return {key.upper(): str(data[key]) for key in data}


def create_config_dict(override: dict = {}) -> dict:
    data = {
        "project_name": "FastAPI-POC",
        "api_docs_enabled": False,
        "db_url": "mongodb://admin:password@db:27017",
        "cache_url": "redis://cache:6379",
        "cache_ttl_user": 1800,
        "access_token_expire_min": 60,
        "refresh_token_expire_min": 180,
        "jwt_algorithm": "HS256",
        "jwt_secret_key": "changethis",
        "username_min_length": 4,
        "password_min_length": 4,
    }

    for key in override:
        data[key] = override[key]

    return data


def password_hash_str():

    return "$2b$12$h.0wMdi.73dhVqlDgNhZH.hDfFcxcvx0RA6doJOlqfh8ufDAy3D1W"


def user_db_dict():

    return {
        "username": "tester",
        "first_name": "Joe",
        "last_name": "Tester",
        "email": "tester@example.com",
        "verified_email": "tester@example.com",
        "roles": ["USER"],
        "disabled": False,
        "date_created": datetime(2020, 1, 1, 0, 0),
        "date_modified": datetime(2020, 1, 2, 0, 0),
        "last_login": datetime(2020, 1, 3, 0, 0),
        "password_hash": password_hash_str(),
    }


def access_token_id_str():

    return "ed2b5f55-79ec-4cb0-ae5b-fbb2a9add283"


def access_token_refreshed_id_str():

    return "fb28b5c4-52c0-49d8-9cfa-b8b150391057"


def refresh_token_id_str():

    return "7399a4d8-0c33-4f89-9212-9194fd91b886"
