from fastapi import FastAPI

from app.core.api.middleware import middlewares
from app.core.api.router import router
from app.core.config import app_settings
from app.core.db.initialize import init_db
from app.core.exception import register_exceptions
from app.core.logging import get_logger

logger = get_logger(__name__)


def app_setup() -> FastAPI:
    fastapi_app = FastAPI(middleware=middlewares, **app_settings())
    fastapi_app.include_router(router)
    register_exceptions(fastapi_app)

    return fastapi_app


app = app_setup()


@app.on_event("startup")
async def app_init():
    logger.info("App initializing")
    return await init_db(app)
