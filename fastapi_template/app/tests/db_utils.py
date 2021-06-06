import logging

from couchbase.n1ql import N1QLQuery

from app.core.db.db_utils import get_db_context
from app.core.models.user import USER_DOC_TYPE
from app.tests.utils import TEST_EMAIL_SUFFIX, TEST_USER_PREFIX

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def clean_up_db():
    db_context = await get_db_context()
    query = f"delete from {db_context.config.cb_bucket} where type = '{USER_DOC_TYPE}' \
        and username like '{TEST_USER_PREFIX}%' and email like '%{TEST_EMAIL_SUFFIX}' returning *"
    n1ql_query = N1QLQuery(query)
    results = db_context.bucket.n1ql_query(n1ql_query)
    docs = []
    async for row in results:
        docs.append(row)
    logger.debug(f"deleted {len(docs)} test users")
