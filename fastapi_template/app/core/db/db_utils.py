import logging

from acouchbase.bucket import Bucket

from app.core.db.config import couchbase_config
from app.core.db.models import DbContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_bucket():
    logger.debug("get_bucket()")
    bucket = Bucket(
        f"{couchbase_config.cb_cluster_url}/{couchbase_config.cb_bucket}",
        username=couchbase_config.cb_app_user,
        password=couchbase_config.cb_app_password,
    )
    await bucket.connect()
    return bucket


async def get_db_context():
    logger.debug("get_db_context()")
    bucket = await get_bucket()
    return DbContext(bucket=bucket, config=couchbase_config)
