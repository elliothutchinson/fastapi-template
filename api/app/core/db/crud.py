from typing import List, Optional, Type

import orjson
from asyncpg.exceptions import UniqueViolationError

from app.core.model import PydanticModel

from .model import DbContext, ResourceAlreadyExistsException
from .service import execute


async def get_doc(
    db_context: DbContext, doc_id: str, doc_model: Type[PydanticModel]
) -> Optional[PydanticModel]:
    doc = None
    async with db_context.connection() as conn:
        query = f"select * from {db_context.config.db_table} where doc_id=$1"
        row = await execute(connection=conn, query=query, params=[doc_id])
        if row:
            json_data = row["doc"]
            json_dict = orjson.loads(json_data)
            doc = doc_model(**json_dict)
    return doc


async def create_doc(
    db_context: DbContext, doc_id: str, doc: PydanticModel
) -> PydanticModel:
    json_data = orjson.dumps(doc.dict())
    async with db_context.connection() as conn:
        query = (
            f"insert into {db_context.config.db_table} (doc_id, doc) values ($1, $2)"
        )
        try:
            await execute(
                connection=conn, query=query, params=[doc_id, json_data.decode()]
            )
        except UniqueViolationError:
            raise ResourceAlreadyExistsException(
                f"Resource with doc_id '{doc_id}' already exists"
            )
    return doc


async def update_doc(
    db_context: DbContext,
    doc_id: str,
    doc: PydanticModel,
    doc_updated: PydanticModel,
) -> PydanticModel:
    doc_merged = doc.copy(update=doc_updated.dict(exclude_defaults=True))
    json_data = orjson.dumps(doc_merged.dict())
    async with db_context.connection() as conn:
        query = f"update {db_context.config.db_table} set doc=$1 where doc_id=$2"
        await execute(connection=conn, query=query, params=[json_data.decode(), doc_id])
    return doc_merged


async def remove_doc(
    db_context: DbContext,
    doc_id: str,
    doc_model: Type[PydanticModel],
) -> Optional[PydanticModel]:
    doc = await get_doc(db_context=db_context, doc_id=doc_id, doc_model=doc_model)
    if doc:
        async with db_context.connection() as conn:
            query = f"delete from {db_context.config.db_table} where doc_id=$1"
            await execute(connection=conn, query=query, params=[doc_id])
    return doc


def build_query(
    db_context: DbContext,
    doc_type: str,
    where_clause: str = None,
    order_by: str = None,
    limit: int = None,
    offset: int = None,
) -> str:
    limit_rows = ""
    if limit:
        limit_rows = f"limit {limit}"
    offset_rows = ""
    if offset:
        offset_rows = f"offset {offset}"

    order = ""
    if order_by:
        order = f"order by {order_by}"
    where = ""
    if where_clause:
        where = f"and {where_clause}"
    query = f"""
            select doc from {db_context.config.db_table}
            where doc->>'type'='{doc_type}' {where} {order} {limit_rows} {offset_rows}
            """
    return query


async def query_doc(
    db_context: DbContext,
    doc_type: str,
    doc_model: Type[PydanticModel],
    where_clause: str = None,
    where_values: List[str] = [],
    order_by: str = None,
    limit: int = None,
    offset: int = None,
) -> List[PydanticModel]:
    query = build_query(
        db_context=db_context,
        doc_type=doc_type,
        where_clause=where_clause,
        order_by=order_by,
        limit=limit,
        offset=offset,
    )
    docs = []
    async with db_context.connection() as conn:
        rows = await execute(
            connection=conn, query=query, params=where_values, fetch_many=True
        )
        if rows:
            for row in rows:
                json_data = row["doc"]
                json_dict = orjson.loads(json_data)
                doc = doc_model(**json_dict)
                docs.append(doc)
    return docs
