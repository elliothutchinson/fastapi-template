import logging
from contextlib import asynccontextmanager

import asyncpg

from app.core.db.config import postgres_config
from app.core.db.models import DbContext, PostgresConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_db_context():
    logger.debug("get_db_context()")
    connection = connection_manager(postgres_config=postgres_config)
    return DbContext(config=postgres_config, connection=connection)


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
