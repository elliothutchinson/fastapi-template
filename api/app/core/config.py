from .model import CoreConfig
from .util import populate_from_env_var


def get_core_config() -> CoreConfig:
    defaults = {
        "username_min_length": 1,
        "password_min_length": 4,
        "project_name": "API Template",
        "login_token_expire_min": 1440.0,
        "secret_key": "changethis",
        "token_path": "/token",
        "login_path": "/login",
        "forgot_path": "/forgot",
        "reset_path": "/reset",
        "user_path": "/user",
        "current_api": "API_V1",
        "api_v1": "/api/v1",
    }
    core_config = CoreConfig(**defaults)
    populate_from_env_var(core_config)
    return core_config
