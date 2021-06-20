from fastapi import APIRouter

from app.core.logger import get_logger
from app.ext.config import ext_config
from app.ext.todos.api import graphql_router as todos_router

logger = get_logger(__name__)


api_router = APIRouter()
api_router.include_router(todos_router, prefix=ext_config.todos_path)
