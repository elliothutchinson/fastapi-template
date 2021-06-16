import logging

from app.core.db.db_utils import (
    connection_manager,
    get_db_context as get_db_context_main,
)
from app.core.db.models import DbContext, PostgresConfig
from app.core.models.user import USER_DOC_TYPE
from app.core.utils import populate_from_env_var
from app.tests.utils import TEST_USER_PREFIX

postgres_config = PostgresConfig()
populate_from_env_var(postgres_config)
postgres_config.pg_table = postgres_config.pg_test_table

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_db_context():
    connection = connection_manager(postgres_config=postgres_config)
    return DbContext(config=postgres_config, connection=connection)


async def clean_up_db(use_test_db: bool = True):
    db_context = await get_db_context() if use_test_db else await get_db_context_main()
    query = f"""
            delete from {db_context.config.pg_table}
            where doc->>'type'='{USER_DOC_TYPE}'
            and doc->>'username' like '{TEST_USER_PREFIX}%'
            and doc->>'email' like '{TEST_USER_PREFIX}%'
            """
    async with db_context.connection() as conn:
        result = await conn.execute(query)
        if result:
            logger.error(f"Deleted test users result: {result}")
        else:
            logger.error("Issue deleting test users")
