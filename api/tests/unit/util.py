from pydantic import SecretStr


def access_token_id():
    return "ae7869b8-dcc4-4330-8222-6d6233a19a20"


def refresh_token_id():
    return "c7bbb603-e4c2-4d4e-a2d0-eae92683f176"


def convert_to_env_vars(data: dict) -> dict:
    return {
        key.upper(): data[key].get_secret_value()
        if isinstance(data[key], SecretStr)
        else str(data[key])
        for key in data
    }
