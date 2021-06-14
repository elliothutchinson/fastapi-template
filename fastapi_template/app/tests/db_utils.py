import logging

from app.core.db.db_utils import get_db_context
from app.core.models.user import USER_DOC_TYPE
from app.tests.utils import TEST_USER_PREFIX

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def clean_up_db():
    db_context = await get_db_context()
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
