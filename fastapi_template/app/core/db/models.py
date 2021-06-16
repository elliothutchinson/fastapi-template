from typing import Any

from pydantic import BaseModel


class PostgresConfig(BaseModel):
    pg_host: str = "pg"
    pg_port: int = 5432
    postgres_user: str = "root"
    postgres_password: str = "password"
    pg_app_user: str = "appuser"
    pg_app_password: str = "password"
    pg_db: str = "api"
    pg_table: str = "docs"
    pg_test_table: str = "test_docs"


class DbContext(BaseModel):
    config: PostgresConfig
    connection: Any
