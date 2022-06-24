from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core import logger as trace
from app.core.logger import get_logger

logger = get_logger(__name__)

# todo: intercept requests for unverified, disabled, etc users

class CustomHeaderMiddleware(BaseHTTPMiddleware):
    @trace.debug(logger)
    async def dispatch(self, request, call_next):
        # logger.info(f"middleware::request {request.url.path}")
        response = await call_next(request)
        response.headers["Custom"] = "Custom Header Example"
        return response


middlewares = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
    Middleware(CustomHeaderMiddleware),
]
