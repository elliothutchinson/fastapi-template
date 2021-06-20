from functools import lru_cache

from app.core.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=None)
def fetch_data(name):
    logger.info(".....fetching data from server")
    return "hello " + name
