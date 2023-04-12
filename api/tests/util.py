import orjson
from pydantic import SecretStr


def password_hash():
    "bcrypt encrypted hash for 'password'"
    return "$2b$12$h.0wMdi.73dhVqlDgNhZH.hDfFcxcvx0RA6doJOlqfh8ufDAy3D1W"


def authorization_header(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


def convert_secret_str(data: dict):
    for key, value in data.items():
        if isinstance(value, SecretStr):
            data[key] = value.get_secret_value()


def json_dict(data: dict | list[dict]) -> dict | list[dict]:
    if isinstance(data, dict):
        convert_secret_str(data)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                convert_secret_str(item)

    json = orjson.dumps(data).decode()
    return orjson.loads(json)
