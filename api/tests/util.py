from typing import List

import orjson


def password_hash():
    "bcrypt encrypted hash for 'password'"
    return "$2b$12$h.0wMdi.73dhVqlDgNhZH.hDfFcxcvx0RA6doJOlqfh8ufDAy3D1W"


def authorization_header(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


def json_dict(data: dict | List[dict]) -> dict | List[dict]:
    json = orjson.dumps(data).decode()
    return orjson.loads(json)
