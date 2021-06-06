import logging

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomHeaderMiddleware(BaseHTTPMiddleware):
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
