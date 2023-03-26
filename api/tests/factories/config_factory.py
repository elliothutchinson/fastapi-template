from pydantic import SecretStr

from app.core.config import Config

from .base_factory import BaseFactory


class ConfigFactory(BaseFactory):
    project_name = "FastAPI-Template"
    api_docs_enabled = False
    db_url = "mongodb://admin:password@db:27017"
    cache_url = "redis://cache:6379"
    cache_ttl_user = 1800
    access_token_expire_min = 60
    refresh_token_expire_min = 180
    jwt_algorithm = "HS256"
    jwt_secret_key = SecretStr("changethis")
    username_min_length = 4
    password_min_length = 4

    class Meta:
        model = Config
