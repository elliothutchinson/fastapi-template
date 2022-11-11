from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import get_config
from app.core.security.token import RevokedTokenDb
from app.core.user.model import UserDb


# todo: return type
def doc_models():

    return [UserDb, RevokedTokenDb]


async def init_db(app) -> bool:
    config = get_config()
    app.db = AsyncIOMotorClient(config.db_url).account
    await init_beanie(app.db, document_models=doc_models())

    return True
