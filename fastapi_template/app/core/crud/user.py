from datetime import datetime

from app.core import logger as trace
from app.core.db.crud_utils import get_doc, insert, run_query, update
from app.core.db.db_utils import get_db_context
from app.core.db.models import DbContext
from app.core.exception import get_already_exists_exception
from app.core.logger import get_logger
from app.core.models.user import (
    USER_DOC_TYPE,
    UserCreate,
    UserDb,
    UserUpdate,
    UserUpdateDb,
    UserUpdatePrivate,
)
from app.core.security.crypt import get_password_hash

logger = get_logger(__name__)


@trace.debug(logger)
def get_user_doc_id(username: str):
    return f"{USER_DOC_TYPE}::{username}"


@trace.debug(logger)
async def get_user_by_email(email: str):
    db_context = await get_db_context()
    return await get_user_by_email_from_db(db_context=db_context, email=email)


@trace.debug(logger)
async def get_user_by_email_from_db(db_context: DbContext, email: str):
    users = await run_query(
        db_context=db_context,
        doc_type=USER_DOC_TYPE,
        doc_model=UserDb,
        where_clause="doc->>'email'=$1",
        where_values=[email],
        limit=1,
    )
    user = None
    if len(users) > 0:
        user = users[0]
    return user


@trace.debug(logger)
async def get_user(username: str):
    db_context = await get_db_context()
    return await get_user_from_db(db_context=db_context, username=username)


@trace.debug(logger)
async def get_user_from_db(db_context: DbContext, username: str):
    doc_id = get_user_doc_id(username)
    return await get_doc(db_context=db_context, doc_id=doc_id, doc_model=UserDb)


@trace.debug(logger)
async def update_user(username: str, user_update: UserUpdate):
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


@trace.debug(logger)
async def update_user_in_db(
    db_context: DbContext, username: str, user_update: UserUpdate
):
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
    )


@trace.debug(logger)
async def update_user_private(username: str, user_update: UserUpdatePrivate):
    db_context = await get_db_context()
    return await update_user_private_in_db(
        db_context=db_context, username=username, user_update=user_update
    )


@trace.debug(logger)
async def update_user_private_in_db(
    db_context: DbContext, username: str, user_update: UserUpdatePrivate
):
    doc_id = get_user_doc_id(username)
    user = await get_user_from_db(db_context=db_context, username=username)
    user_update_db = UserUpdateDb(**user_update.dict())
    return await update(
        db_context=db_context,
        doc_id=doc_id,
        doc=user,
        doc_updated=user_update_db,
    )


@trace.debug(logger)
async def create_user(user_create: UserCreate):
    db_context = await get_db_context()
    existing_user = await get_user_by_email_from_db(
        db_context=db_context, email=user_create.email
    )
    if existing_user:
        raise get_already_exists_exception("An account already exists with this email")
    return await create_user_in_db(db_context=db_context, user_create=user_create)


@trace.debug(logger)
async def create_user_in_db(db_context: DbContext, user_create: UserCreate):
    doc_id = get_user_doc_id(user_create.username)
    password_hash = get_password_hash(user_create.password)
    user_db = UserDb(
        **user_create.dict(), date_created=datetime.now(), hashed_password=password_hash
    )
    return await insert(db_context=db_context, doc_id=doc_id, doc_in=user_db)
