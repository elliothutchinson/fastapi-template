from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import get_config
from app.core.todo.repo import TodoDb, TodoListDb
from app.core.user.repo import UserDb


def doc_models() -> list[Document]:
    return [UserDb, TodoListDb, TodoDb]


async def init_db(app) -> bool:
    config = get_config()
    app.db = AsyncIOMotorClient(config.db_url).api
    await init_beanie(app.db, document_models=doc_models())

    return True
