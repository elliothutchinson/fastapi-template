import logging
from datetime import datetime

from app.core.db.crud_utils import get_doc, insert, run_query, update
from app.core.db.db_utils import get_db_context
from app.core.db.models import DbContext
from app.core.exception import get_already_exists_exception
from app.core.models.user import (
    USER_DOC_TYPE,
    UserCreate,
    UserDb,
    UserUpdate,
    UserUpdateDb,
    UserUpdatePrivate,
)
from app.core.models.utils import get_model_fields
from app.core.security.crypt import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_user_doc_id(username: str):
    logger.debug("get_user_doc_id()")
    return f"{USER_DOC_TYPE}::{username}"


async def get_user_by_email(email: str):
    logger.debug("get_user_by_email()")
    db_context = await get_db_context()
    return await get_user_by_email_from_db(db_context=db_context, email=email)


async def get_user_by_email_from_db(db_context: DbContext, email: str):
    logger.debug("get_user_by_email_from_db()")
    select_fields = get_model_fields(model=UserDb)
    users = await run_query(
        db_context=db_context,
        doc_type=USER_DOC_TYPE,
        doc_model=UserDb,
        select_fields=select_fields,
        where_clause="email=$1",
        where_values=[email],
        limit=1,
    )
    user = None
    if len(users) > 0:
        user = users[0]
    return user


async def get_user(username: str):
    logger.debug("get_user()")
    db_context = await get_db_context()
    return await get_user_from_db(db_context=db_context, username=username)


async def get_user_from_db(db_context: DbContext, username: str):
    logger.debug("get_user_from_db()")
    doc_id = get_user_doc_id(username)
    return await get_doc(db_context=db_context, doc_id=doc_id, doc_model=UserDb)


async def update_user(username: str, user_update: UserUpdate):
    logger.debug("update_user()")
    db_context = await get_db_context()
    if user_update.email:
        existing_user = await get_user_by_email_from_db(
            db_context=db_context, email=user_update.email
        )
        if existing_user and existing_user.username != username:
            raise get_already_exists_exception(
                "An account already exists with this email"
            )
    return await update_user_in_db(
        db_context=db_context, username=username, user_update=user_update
    )


async def update_user_in_db(
    db_context: DbContext, username: str, user_update: UserUpdate, persist_to=0
):
    logger.debug("update_user_in_db()")
    doc_id = get_user_doc_id(username)
    user = await get_user_from_db(db_context=db_context, username=username)
    hashed_password = None
    if user_update.password:
        hashed_password = get_password_hash(user_update.password)
    user_update_db = UserUpdateDb(
        **user_update.dict(),
        date_modified=datetime.now(),
        hashed_password=hashed_password,
    )
    return await update(
        db_context=db_context,
        doc_id=doc_id,
        doc=user,
        doc_updated=user_update_db,
        persist_to=persist_to,
    )


async def update_user_private(username: str, user_update: UserUpdatePrivate):
    logger.debug("update_user_private()")
    db_context = await get_db_context()
    return await update_user_private_in_db(
        db_context=db_context, username=username, user_update=user_update
    )


async def update_user_private_in_db(
    db_context: DbContext, username: str, user_update: UserUpdatePrivate, persist_to=0
):
    logger.debug("update_user_private_in_db()")
    doc_id = get_user_doc_id(username)
    user = await get_user_from_db(db_context=db_context, username=username)
    user_update_db = UserUpdateDb(**user_update.dict())
    return await update(
        db_context=db_context,
        doc_id=doc_id,
        doc=user,
        doc_updated=user_update_db,
        persist_to=persist_to,
    )


async def create_user(user_in: UserCreate):
    logger.debug("create_user()")
    db_context = await get_db_context()
    existing_user = await get_user_by_email_from_db(
        db_context=db_context, email=user_in.email
    )
    if existing_user:
        raise get_already_exists_exception("An account already exists with this email")
    return await insert_user_in_db(db_context=db_context, user_in=user_in)


async def insert_user_in_db(db_context: DbContext, user_in: UserCreate, persist_to=0):
    logger.debug("insert_user_in_db()")
    doc_id = get_user_doc_id(user_in.username)
    password_hash = get_password_hash(user_in.password)
    user_db = UserDb(
        **user_in.dict(), date_created=datetime.now(), hashed_password=password_hash
    )
    return await insert(
        db_context=db_context, doc_id=doc_id, doc_in=user_db, persist_to=persist_to
    )
