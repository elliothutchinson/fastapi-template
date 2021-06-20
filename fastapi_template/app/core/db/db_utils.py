from contextlib import asynccontextmanager

import asyncpg

from app.core import logger as trace
from app.core.db.config import postgres_config
from app.core.db.models import DbContext, PostgresConfig
from app.core.logger import get_logger

logger = get_logger(__name__)


@trace.debug(logger)
async def get_db_context():
    connection = connection_manager(postgres_config=postgres_config)
    return DbContext(config=postgres_config, connection=connection)


@trace.debug(logger)
def connection_manager(postgres_config: PostgresConfig):
    @asynccontextmanager
    async def get_connection():
        logger.debug("get_connection()")
        conn = None
        try:
            conn = await asyncpg.connect(
                host=postgres_config.pg_host,
                port=postgres_config.pg_port,
                user=postgres_config.pg_app_user,
                password=postgres_config.pg_app_password,
                database=postgres_config.pg_db,
            )
            yield conn
        finally:
            logger.debug("get_connection::closing connection")
            if conn:
                await conn.close()

    return get_connection
