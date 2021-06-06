import logging
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def fetch_data(name):
    logger.info(".....fetching data from server")
    return "hello " + name
