from datetime import datetime
from typing import Optional

from pydantic import EmailStr

from app.core.api.security import crypt
from app.core.db import crud as db_crud
from app.core.db.model import (
    DbContext,
    ResourceAlreadyExistsException,
    ResourceNotFoundException,
)

from .model import (
    USER_DOC_TYPE,
    UserCreate,
    UserDb,
    UserUpdate,
    UserUpdateDb,
    UserUpdatePrivate,
)


def get_user_doc_id(username: str) -> str:
    return f"{USER_DOC_TYPE}::{username}"


async def get_user(db_context: DbContext, username: str) -> Optional[UserDb]:
    doc_id = get_user_doc_id(username=username)
    return await db_crud.get_doc(db_context=db_context, doc_id=doc_id, doc_model=UserDb)


async def get_user_by_email(db_context: DbContext, email: EmailStr) -> Optional[UserDb]:
    users = await db_crud.query_doc(
        db_context=db_context,
        doc_type=USER_DOC_TYPE,
        doc_model=UserDb,
        where_clause="doc->>'email'=$1",
        where_values=[email],
        order_by="doc->>'date_created'",
        limit=1,
    )
    user = None
    if users:
        user = users[0]
    return user


async def create_user(db_context: DbContext, user_create: UserCreate) -> UserDb:
    existing_user = await get_user_by_email(
        db_context=db_context, email=user_create.email
    )
    if existing_user:
        raise ResourceAlreadyExistsException(
            "An account already exists with this email"
        )

    password_hash = crypt.hash_password(password=user_create.password)
    user_db = UserDb(
        **user_create.dict(), date_created=datetime.now(), password_hash=password_hash
    )

    doc_id = get_user_doc_id(username=user_create.username)
    return await db_crud.create_doc(db_context=db_context, doc_id=doc_id, doc=user_db)


async def validate_email_update(
    db_context: DbContext, update_email: EmailStr, current_email: EmailStr
) -> Optional[bool]:
    if update_email and update_email != current_email:
        existing_user = await get_user_by_email(
            db_context=db_context, email=update_email
        )
        if existing_user:
            raise ResourceAlreadyExistsException(
                f"An account already exists with email {update_email}"
            )
        return True


async def update_user(
    db_context: DbContext, username: str, user_update: UserUpdate
) -> UserDb:
    user = await get_user(db_context=db_context, username=username)
    if not user:
        raise ResourceNotFoundException("User not found")

    await validate_email_update(
        db_context=db_context, update_email=user_update.email, current_email=user.email
    )

    password_hash = None
    if user_update.password:
        password_hash = crypt.hash_password(password=user_update.password)

    user_update_db = UserUpdateDb(
        **user_update.dict(),
        date_modified=datetime.now(),
        password_hash=password_hash,
    )

    doc_id = get_user_doc_id(username=username)
    return await db_crud.update_doc(
        db_context=db_context,
        doc_id=doc_id,
        doc=user,
        doc_updated=user_update_db,
    )


async def update_user_private(
    db_context: DbContext, username: str, user_update_private: UserUpdatePrivate
) -> UserDb:
    user = await get_user(db_context=db_context, username=username)
    if not user:
        raise ResourceNotFoundException("User not found")

    user_update_db = UserUpdateDb(
        **user_update_private.dict(),
    )

    doc_id = get_user_doc_id(username=username)
    return await db_crud.update_doc(
        db_context=db_context,
        doc_id=doc_id,
        doc=user,
        doc_updated=user_update_db,
    )
