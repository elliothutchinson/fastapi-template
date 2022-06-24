from typing import Callable

from pydantic import BaseModel, SecretStr


class DbConfig(BaseModel):
    db_host: str
    db_port: int
    db_root_user: str
    db_root_password: SecretStr
    db_root_database: str
    db_app_user: str
    db_app_password: SecretStr
    db_app_database: str
    db_table: str
    db_test_table: str


class DbConnect(BaseModel):
    host: str
    port: int
    user: str
    password: SecretStr
    database: str


class DbContext(BaseModel):
    config: DbConfig
    connection: Callable


class ResourceAlreadyExistsException(Exception):
    pass


class ResourceNotFoundException(Exception):
    pass
