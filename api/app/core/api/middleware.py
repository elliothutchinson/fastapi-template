from contextvars import ContextVar
from uuid import uuid4

from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_config
from app.core.logging import get_logger

logger = get_logger(__name__)

config = get_config

ctx_request_id = ContextVar("request_id", default="n/a")
ctx_request_ip = ContextVar("request_ip", default="n/a")


class RequestIdMiddleware(BaseHTTPMiddleware):  # pylint: disable=too-few-public-methods
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("request_id", str(uuid4()))
        ctx_request_id.set(request_id)

        # todo: update tests
        request_ip = "n/a"
        if hasattr(request.client, "host"):
            request_ip = request.client.host
        ctx_request_ip.set(request_ip)

        response = await call_next(request)
        response.headers["request_id"] = request_id

        return response


middlewares = [
    Middleware(RequestIdMiddleware),
]
