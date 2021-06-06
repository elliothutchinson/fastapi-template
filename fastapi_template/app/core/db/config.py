import logging

from app.core.db.models import CouchbaseConfig
from app.core.utils import populate_from_env_var

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

couchbase_config = CouchbaseConfig()
populate_from_env_var(couchbase_config)
