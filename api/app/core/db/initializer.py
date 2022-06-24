import asyncio
import logging

from asyncpg import InvalidCatalogNameError

from .config import get_db_config
from .model import DbConfig, DbContext
from .service import get_db_connect_app_user, get_db_connect_root_user, get_db_context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    logger.info("init_db()")
    db_config = get_db_config()
    asyncio.run(config_db(db_config=db_config))
    return True


async def config_db(db_config: DbConfig):
    logger.info("config_db()")
    root_user_connect = get_db_connect_root_user(db_config=db_config)
    root_user_context = get_db_context(db_connect=root_user_connect)
    await create_user_if_not_exists(db_context=root_user_context)

    app_user_connect = get_db_connect_app_user(db_config=db_config)
    app_user_context = get_db_context(db_connect=app_user_connect)

    await create_db_if_not_exists(
        app_user_context=app_user_context, root_user_context=root_user_context
    )

    await create_table_if_not_exists(
        db_context=app_user_context, table=db_config.db_table
    )
    await create_table_if_not_exists(
        db_context=app_user_context, table=db_config.db_test_table
    )

    return True


async def create_user_if_not_exists(db_context: DbContext):
    logger.info("create_user_if_not_exists()")
    user_created = False
    if not await user_exists(db_context=db_context):
        user_created = await create_user(db_context=db_context)
    logger.info(f"user_created: {user_created}")
    return user_created


async def user_exists(db_context: DbContext):
    logger.info("user_exists()")
    user_exists = False
    async with db_context.connection() as conn:
        row = await conn.fetchrow(
            f"select rolname from pg_roles where rolname='{db_context.config.db_app_user}'"
        )
        if row:
            user_exists = True
    logger.info(f"user_exists: {user_exists}")
    return user_exists


async def create_user(db_context: DbContext):
    logger.info("create_user()")
    async with db_context.connection() as conn:
        await conn.execute(
            f"create user {db_context.config.db_app_user} with password '{db_context.config.db_app_password.get_secret_value()}'"
        )
    return True


async def create_db_if_not_exists(
    app_user_context: DbContext, root_user_context: DbContext
):
    logger.info("create_db_if_not_exists()")
    db_created = False
    if not await db_exists(db_context=app_user_context):
        db_created = await create_db(db_context=root_user_context)
    logger.info(f"db_created: {db_created}")
    return db_created


async def db_exists(db_context: DbContext):
    logger.info("db_exists()")
    db_exists = False
    try:
        async with db_context.connection():
            db_exists = True
    except InvalidCatalogNameError:
        pass
    logger.info(f"db_exists: {db_exists}")
    return db_exists


async def create_db(db_context: DbContext):
    logger.info("create_db()")
    async with db_context.connection() as conn:
        await conn.execute(
            f'create database "{db_context.config.db_app_database}" owner "{db_context.config.db_app_user}"'
        )
    return True


async def create_table_if_not_exists(db_context: DbContext, table: str):
    logger.info("create_table_if_not_exists()")
    table_created = False
    if not await table_exists(db_context=db_context, table=table):
        table_created = await create_table(db_context=db_context, table=table)
    logger.info(f"table_created: {table_created}")
    return table_created


async def table_exists(db_context: DbContext, table: str):
    logger.info("table_exists()")
    table_created = False
    async with db_context.connection() as conn:
        row = await conn.fetchrow(
            f"select table_name from information_schema.tables where table_name='{table}'"
        )
        if row:
            logger.info(f"row: {row}")
            table_created = True
    logger.info(f"table_created: {table_created}")
    return table_created


async def create_table(db_context: DbContext, table: str):
    logger.info("create_table()")
    async with db_context.connection() as conn:
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
    return True


if __name__ == "__main__":
    init_db()
