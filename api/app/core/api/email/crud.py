from typing import List

from app.core.db import crud as db_crud
from app.core.db.model import DbContext

from .model import EMAIL_DOC_TYPE, EmailDb


def get_email_doc_id(email_id: str) -> str:
    return f"{EMAIL_DOC_TYPE}::{email_id}"


async def create_email(db_context: DbContext, email_db: EmailDb) -> EmailDb:
    doc_id = get_email_doc_id(email_id=email_db.email_id)
    return await db_crud.create_doc(db_context=db_context, doc_id=doc_id, doc=email_db)


async def get_emails_for_user(db_context: DbContext, username: str) -> List[EmailDb]:
    return await db_crud.query_doc(
        db_context=db_context,
        doc_type=EMAIL_DOC_TYPE,
        doc_model=EmailDb,
        where_clause="doc->>'username'=$1",
        where_values=[username],
        order_by="doc->>'date_created'",
    )
