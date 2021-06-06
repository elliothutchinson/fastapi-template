import logging

from fastapi import APIRouter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


api_router = APIRouter()
