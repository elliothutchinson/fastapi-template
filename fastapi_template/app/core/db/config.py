import logging

from app.core.db.models import PostgresConfig
from app.core.utils import populate_from_env_var

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


postgres_config = PostgresConfig()
populate_from_env_var(postgres_config)
