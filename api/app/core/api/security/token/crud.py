from typing import List

from app.core.db import crud as db_crud
from app.core.db.model import DbContext

from .model import TOKEN_DOC_TYPE, TokenDb, TokenUpdateDb


def get_token_doc_id(token_id: str) -> str:
    return f"{TOKEN_DOC_TYPE}::{token_id}"


async def create_token(db_context: DbContext, token_db: TokenDb) -> TokenDb:
    doc_id = get_token_doc_id(token_id=token_db.token_id)
    return await db_crud.create_doc(db_context=db_context, doc_id=doc_id, doc=token_db)


async def update_token(
    db_context: DbContext, token_db: TokenDb, token_update_db: TokenUpdateDb
) -> TokenDb:
    doc_id = get_token_doc_id(token_id=token_db.token_id)
    return await db_crud.update_doc(
        db_context=db_context,
        doc_id=doc_id,
        doc=token_db,
        doc_updated=token_update_db,
    )


async def get_valid_tokens_for_user(
    db_context: DbContext, username: str
) -> List[TokenDb]:
    return await db_crud.query_doc(
        db_context=db_context,
        doc_type=TOKEN_DOC_TYPE,
        doc_model=TokenDb,
        where_clause="doc->>'username'=$1 and doc->>'date_redacted' is null and doc->>'date_expires' > NOW()",
        where_values=[username],
        order_by="doc->>'date_created'",
    )
