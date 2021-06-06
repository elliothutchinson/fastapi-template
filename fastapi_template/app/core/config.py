import logging

from app.core.models.core_config import CoreConfig
from app.core.utils import populate_from_env_var

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

core_config = CoreConfig()
populate_from_env_var(core_config)
