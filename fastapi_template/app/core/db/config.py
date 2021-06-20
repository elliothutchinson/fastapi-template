from app.core.db.models import PostgresConfig
from app.core.logger import get_logger
from app.core.utils import populate_from_env_var

logger = get_logger(__name__)


postgres_config = PostgresConfig()
populate_from_env_var(postgres_config)
