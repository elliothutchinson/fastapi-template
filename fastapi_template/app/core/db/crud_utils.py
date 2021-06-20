import json
from typing import List, Optional, Type, Union

from asyncpg.exceptions import UniqueViolationError
from fastapi.encoders import jsonable_encoder

from app.core import logger as trace
from app.core.db.models import DbContext
from app.core.exception import get_already_exists_exception
from app.core.logger import get_logger
from app.core.models.utils import PydanticModel

logger = get_logger(__name__)


@trace.debug(logger)
async def get_doc(
    db_context: DbContext, doc_id: str, doc_model: Type[PydanticModel] = None
) -> Optional[Union[PydanticModel, dict]]:
    async with db_context.connection() as conn:
        query = f"select * from {db_context.config.pg_table} where doc_id=$1"
        stmt = await conn.prepare(query)
        row = await stmt.fetchrow(doc_id)
        if not row:
            return None
        doc_str = row["doc"]
        json_dict = json.loads(doc_str)
        if not doc_model:
            return json_dict
        model = doc_model(**json_dict)
        return model


@trace.debug(logger)
async def insert(
    db_context: DbContext, doc_id: str, doc_in: PydanticModel
) -> Optional[PydanticModel]:
    doc_data = jsonable_encoder(doc_in)
    json_data = json.dumps(doc_data)
    async with db_context.connection() as conn:
        try:
            query = f"insert into {db_context.config.pg_table} (doc_id, doc) values ($1, $2)"
            stmt = await conn.prepare(query)
            await stmt.fetchrow(doc_id, json_data)
            return doc_in
        except UniqueViolationError:
            raise get_already_exists_exception("Resource already exists")


@trace.debug(logger)
async def update(
    db_context: DbContext,
    doc_id: str,
    doc: PydanticModel,
    doc_updated: PydanticModel,
) -> Optional[PydanticModel]:
    doc_updated = doc.copy(update=doc_updated.dict(exclude_defaults=True))
    doc_data = jsonable_encoder(doc_updated)
    json_data = json.dumps(doc_data)
    async with db_context.connection() as conn:
        query = f"update {db_context.config.pg_table} set doc=$1 where doc_id=$2"
        stmt = await conn.prepare(query)
        await stmt.fetchrow(json_data, doc_id)
        return doc_updated


@trace.debug(logger)
async def remove(
    db_context: DbContext,
    doc_id: str,
    doc_model: Type[PydanticModel] = None,
) -> Optional[Union[PydanticModel, bool]]:
    doc = await get_doc(db_context=db_context, doc_id=doc_id, doc_model=doc_model)
    if not doc:
        return None
    async with db_context.connection() as conn:
        query = f"delete from {db_context.config.pg_table} where doc_id=$1"
        stmt = await conn.prepare(query)
        await stmt.fetchrow(doc_id)
        if doc_model:
            return doc
        return True


@trace.debug(logger)
async def run_query(
    db_context: DbContext,
    doc_type: str,
    doc_model: Type[PydanticModel],
    where_clause: str = None,
    where_values: List[str] = [],
    order_by: str = None,
    limit: int = None,
) -> List[PydanticModel]:
    limit_rows = ""
    if limit:
        limit_rows = f"limit {limit}"
    order = ""
    if order_by:
        order = f"order by {order_by}"
    where = ""
    if where_clause:
        where = f"and {where_clause}"
    query = f"""
            select doc from {db_context.config.pg_table}
            where doc->>'type'='{doc_type}' {where} {order} {limit_rows}
            """
    logger.debug(f"query: {query}")
    logger.debug(f"where_values: {where_values}")
    docs = []
    async with db_context.connection() as conn:
        stmt = await conn.prepare(query)
        rows = await stmt.fetch(*where_values)
        for row in rows:
            logger.debug(f"row: {row}")
            doc_str = row["doc"]
            json_dict = json.loads(doc_str)
            model = doc_model(**json_dict)
            docs.append(model)
    return docs
