from fastapi import APIRouter

from app.core.api.model import ServerResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=ServerResponse)
async def service_health():

    return ServerResponse(message="OK")
