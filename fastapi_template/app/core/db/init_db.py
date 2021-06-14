import asyncio
import logging

import asyncpg

from app.core.db.config import postgres_config
from app.core.db.models import PostgresConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def config_postgres(postgres_config: PostgresConfig):
    logger.debug("config_postgres()")
    if not await is_postgres_user_created(postgres_config=postgres_config):
        await create_postgres_user(postgres_config=postgres_config)
    if not await is_postgres_db_created(postgres_config=postgres_config):
        await create_postgres_db(postgres_config=postgres_config)
    if not await is_postgres_table_created(postgres_config=postgres_config):
        await create_postgres_table(postgres_config=postgres_config)
    return True


async def is_postgres_user_created(postgres_config: PostgresConfig):
    logger.debug("is_postgres_user_created()")
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


async def is_postgres_db_created(postgres_config: PostgresConfig):
    logger.debug("is_postgres_db_created()")
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


async def is_postgres_table_created(postgres_config: PostgresConfig):
    logger.debug("is_postgres_table_created()")
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
            f"select table_name from information_schema.tables where table_name='{postgres_config.pg_table}'"
        )
        if row:
            table_created = True
    finally:
        if conn:
            logger.debug("is_postgres_table_created::closing conn")
            await conn.close()
    logger.debug(f"table_created: {table_created}")
    return table_created


async def create_postgres_user(postgres_config: PostgresConfig):
    logger.debug("create_postgres_user()")
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


async def create_postgres_db(postgres_config: PostgresConfig):
    logger.debug("create_postgres_db()")
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


async def create_postgres_table(postgres_config: PostgresConfig):
    logger.debug("create_postgres_table()")
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
            create table docs (
                doc_id varchar,
                doc jsonb,
                primary key (doc_id)
            )
            """
        )
        await conn.execute(f"create index on docs ((doc->>'type'))")
        table_created = True
    finally:
        if conn:
            logger.debug("create_postgres_table::closing conn")
            await conn.close()
    logger.debug(f"table_created: {table_created}")
    return table_created


def init_db():
    logger.debug("init_db()")

    asyncio.run(config_postgres(postgres_config=postgres_config))


if __name__ == "__main__":
    init_db()
