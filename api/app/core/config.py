from pydantic import BaseModel, SecretStr

from .util import populate_from_env


class Config(BaseModel):
    project_name: str
    api_docs_enabled: bool
    db_url: str
    cache_url: str
    cache_ttl_user: int
    access_token_expire_min: float
    refresh_token_expire_min: float
    jwt_algorithm: str
    jwt_secret_key: SecretStr
    username_min_length: int
    password_min_length: int


def get_config() -> Config:
    env = populate_from_env(Config)

    return Config(**env)


def app_settings() -> dict:
    config = get_config()
    settings = {"title": config.project_name}

    if not config.api_docs_enabled:
        settings["docs_url"] = None
        settings["redoc_url"] = None

    return settings
