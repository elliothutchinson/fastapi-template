import asyncio

import asyncpg

from app.core import logger as trace
from app.core.db.config import postgres_config
from app.core.db.models import PostgresConfig
from app.core.logger import get_logger

logger = get_logger(__name__)


@trace.debug(logger)
async def config_postgres(postgres_config: PostgresConfig):
    if not await is_postgres_user_created(postgres_config=postgres_config):
        await create_postgres_user(postgres_config=postgres_config)
    if not await is_postgres_db_created(postgres_config=postgres_config):
        await create_postgres_db(postgres_config=postgres_config)
    if not await is_postgres_table_created(
        postgres_config=postgres_config, table=postgres_config.pg_table
    ):
        await create_postgres_table(
            postgres_config=postgres_config, table=postgres_config.pg_table
        )
    if not await is_postgres_table_created(
        postgres_config=postgres_config, table=postgres_config.pg_test_table
    ):
        await create_postgres_table(
            postgres_config=postgres_config, table=postgres_config.pg_test_table
        )
    return True


@trace.debug(logger)
async def is_postgres_user_created(postgres_config: PostgresConfig):
    user_created = False
    conn = None
    try:
        conn = await asyncpg.connect(
            host=postgres_config.pg_host,
            port=postgres_config.pg_port,
            user=postgres_config.postgres_user,
            password=postgres_config.postgres_password,
            database="template1",
        )
        row = await conn.fetchrow(
            f"select rolname from pg_roles where rolname='{postgres_config.pg_app_user}'"
        )
        if row:
            user_created = True
    finally:
        if conn:
            logger.debug("is_postgres_user_created::closing conn")
            await conn.close()
    logger.debug(f"user_created: {user_created}")
    return user_created


@trace.debug(logger)
async def is_postgres_db_created(postgres_config: PostgresConfig):
    db_created = False
    conn = None
    try:
        conn = await asyncpg.connect(
            host=postgres_config.pg_host,
            port=postgres_config.pg_port,
            user=postgres_config.postgres_user,
            password=postgres_config.postgres_password,
            database=postgres_config.pg_db,
        )
        db_created = True
    except asyncpg.InvalidCatalogNameError:
        pass
    finally:
        if conn:
            logger.debug("is_postgres_db_created::closing conn")
            await conn.close()
    logger.debug(f"db_created: {db_created}")
    return db_created


@trace.debug(logger)
async def is_postgres_table_created(postgres_config: PostgresConfig, table: str):
    table_created = False
    conn = None
    try:
        conn = await asyncpg.connect(
            host=postgres_config.pg_host,
            port=postgres_config.pg_port,
            user=postgres_config.pg_app_user,
            password=postgres_config.pg_app_password,
            database=postgres_config.pg_db,
        )
        row = await conn.fetchrow(
            f"select table_name from information_schema.tables where table_name='{table}'"
        )
        if row:
            table_created = True
    finally:
        if conn:
            logger.debug("is_postgres_table_created::closing conn")
            await conn.close()
    logger.debug(f"table '{table}' created: {table_created}")
    return table_created


@trace.debug(logger)
async def create_postgres_user(postgres_config: PostgresConfig):
    user_created = False
    conn = None
    try:
        conn = await asyncpg.connect(
            host=postgres_config.pg_host,
            port=postgres_config.pg_port,
            user=postgres_config.postgres_user,
            password=postgres_config.postgres_password,
            database="template1",
        )
        await conn.execute(
            f"create user {postgres_config.pg_app_user} with password '{postgres_config.pg_app_password}'"
        )
        user_created = True
    finally:
        if conn:
            logger.debug("create_postgres_user::closing conn")
            await conn.close()
    logger.debug(f"user_created: {user_created}")
    return user_created


@trace.debug(logger)
async def create_postgres_db(postgres_config: PostgresConfig):
    db_created = False
    conn = None
    try:
        conn = await asyncpg.connect(
            host=postgres_config.pg_host,
            port=postgres_config.pg_port,
            user=postgres_config.postgres_user,
            password=postgres_config.postgres_password,
            database="template1",
        )
        await conn.execute(
            f'create database "{postgres_config.pg_db}" owner "{postgres_config.pg_app_user}"'
        )
        db_created = True
    finally:
        if conn:
            logger.debug("create_postgres_db::closing conn")
            await conn.close()
    logger.debug(f"db_created: {db_created}")
    return db_created


@trace.debug(logger)
async def create_postgres_table(postgres_config: PostgresConfig, table: str):
    table_created = False
    conn = None
    try:
        conn = await asyncpg.connect(
            host=postgres_config.pg_host,
            port=postgres_config.pg_port,
            user=postgres_config.pg_app_user,
            password=postgres_config.pg_app_password,
            database=postgres_config.pg_db,
        )
        await conn.execute(
            f"""
            create table {table} (
                doc_id varchar,
                doc jsonb,
                primary key (doc_id)
            )
            """
        )
        await conn.execute(f"create index on {table} ((doc->>'type'))")
        table_created = True
    finally:
        if conn:
            logger.debug("create_postgres_table::closing conn")
            await conn.close()
    logger.debug(f"table '{table}' created: {table_created}")
    return table_created


@trace.debug(logger)
def init_db():
    asyncio.run(config_postgres(postgres_config=postgres_config))


if __name__ == "__main__":
    init_db()
