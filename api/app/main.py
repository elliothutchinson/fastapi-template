from fastapi import FastAPI

from app.core.api.api import api_router as core_router
from app.core.config import get_core_config

core_config = get_core_config()

app = FastAPI(title=core_config.project_name)

app.include_router(core_router)
