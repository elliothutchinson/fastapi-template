import logging
from contextlib import asynccontextmanager
from typing import AsyncContextManager, Callable, List

import asyncpg

from .config import get_db_config
from .model import DbConfig, DbConnect, DbContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_connect_app_user(db_config: DbConfig) -> DbConnect:
    return DbConnect(
        host=db_config.db_host,
        port=db_config.db_port,
        user=db_config.db_app_user,
        password=db_config.db_app_password,
        database=db_config.db_app_database,
    )


def get_db_connect_root_user(db_config: DbConfig) -> DbConnect:
    return DbConnect(
        host=db_config.db_host,
        port=db_config.db_port,
        user=db_config.db_root_user,
        password=db_config.db_root_password,
        database=db_config.db_root_database,
    )


def get_db_context(db_connect: DbConnect = None) -> DbContext:
    db_config = get_db_config()

    if not db_connect:
        db_connect = get_db_connect_app_user(db_config=db_config)

    connection = connection_manager(db_connect=db_connect)
    return DbContext(config=db_config, connection=connection)


def connection_manager(db_connect: DbConnect) -> Callable:
    @asynccontextmanager
    async def get_connection() -> AsyncContextManager:
        conn = None
        try:
            dbc = db_connect.dict()
            dbc["password"] = db_connect.password.get_secret_value()
            logger.info(f"dbc: {dbc}")
            conn = await asyncpg.connect(**dbc)
            yield conn
        finally:
            if conn:
                await conn.close()

    return get_connection


async def execute(
    connection: Callable, query: str, params: List[str], fetch_many: bool = False
):
    stmt = await connection.prepare(query)
    results = None
    if fetch_many:
        results = await stmt.fetch(*params)
    else:
        results = await stmt.fetchrow(*params)
    return results
