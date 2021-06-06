import logging
from typing import Type, TypeVar

from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PydanticModel = TypeVar("PydanticModel", bound=BaseModel)


def get_model_fields(model: Type[PydanticModel]):
    logger.debug("get_model_fields()")
    return [k for k in model.__fields__.keys()]
