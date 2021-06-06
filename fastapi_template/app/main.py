import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.api.api import api_router as core_router
from app.core.config import core_config
from app.core.middleware import middlewares
from app.ext.api.api import api_router as ext_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=core_config.project_name, middleware=middlewares)

app.include_router(core_router)
app.include_router(ext_router)

app.mount(
    "/dashboard",
    StaticFiles(directory="ui/dashboard/build", html=True),
    name="dashboard",
)

if core_config.debug:
    app.mount("/", StaticFiles(directory="ui/dev", html=True), name="dev")
