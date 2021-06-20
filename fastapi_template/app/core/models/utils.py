from typing import Type, TypeVar

from pydantic import BaseModel

from app.core import logger as trace
from app.core.logger import get_logger

logger = get_logger(__name__)

PydanticModel = TypeVar("PydanticModel", bound=BaseModel)


@trace.debug(logger)
def get_model_fields(model: Type[PydanticModel]):
    return [k for k in model.__fields__.keys()]
