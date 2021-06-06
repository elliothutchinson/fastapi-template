import logging

from app.core.utils import populate_from_env_var
from app.ext.models.ext_config import ExtConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ext_config = ExtConfig()
populate_from_env_var(ext_config)
