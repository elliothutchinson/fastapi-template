from app.core.logger import get_logger
from app.core.models.core_config import CoreConfig
from app.core.utils import populate_from_env_var

logger = get_logger(__name__)

core_config = CoreConfig()
populate_from_env_var(core_config)
