import logging
from typing import List, Optional, Type, Union

from couchbase.exceptions import KeyExistsError
from couchbase.n1ql import N1QLQuery
from fastapi.encoders import jsonable_encoder

from app.core.db.models import DbContext
from app.core.exception import get_already_exists_exception
from app.core.models.utils import PydanticModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_doc(
    db_context: DbContext, doc_id: str, doc_model: Type[PydanticModel]
) -> Optional[PydanticModel]:
    logger.debug("get_doc()")
    result = await db_context.bucket.get(doc_id, quiet=True)
    if not result.value:
        return None
    model = doc_model(**result.value)
    return model


async def insert(
    db_context: DbContext, doc_id: str, doc_in: PydanticModel, persist_to=0, ttl=0
) -> Optional[PydanticModel]:
    logger.debug("insert()")
    doc_data = jsonable_encoder(doc_in)
    with db_context.bucket.durability(
        persist_to=persist_to, timeout=db_context.config.cb_durability_timeout_secs
    ):
        try:
            result = await db_context.bucket.insert(doc_id, doc_data, ttl=ttl)
            if result.success:
                return doc_in
        except KeyExistsError:
            raise get_already_exists_exception("Resource already exists")
    return None


async def upsert(
    db_context: DbContext, doc_id: str, doc_in: PydanticModel, persist_to=0, ttl=0
) -> Optional[PydanticModel]:
    logger.debug("upsert()")
    doc_data = jsonable_encoder(doc_in)
    with db_context.bucket.durability(
        persist_to=persist_to, timeout=db_context.config.cb_durability_timeout_secs
    ):
        result = await db_context.bucket.upsert(doc_id, doc_data, ttl=ttl)
        if result.success:
            return doc_in
    return None


async def update(
    db_context: DbContext,
    doc_id: str,
    doc: PydanticModel,
    doc_updated: PydanticModel,
    persist_to=0,
    ttl=0,
) -> Optional[PydanticModel]:
    logger.debug("update()")
    doc_updated = doc.copy(update=doc_updated.dict(exclude_defaults=True))
    data = jsonable_encoder(doc_updated)
    with db_context.bucket.durability(
        persist_to=persist_to, timeout=db_context.config.cb_durability_timeout_secs
    ):
        result = await db_context.bucket.upsert(doc_id, data, ttl=ttl)
        if result.success:
            return doc_updated
    return None


async def replace(
    db_context: DbContext, doc_id: str, doc_in: PydanticModel, persist_to=0, ttl=0
) -> Optional[PydanticModel]:
    logger.debug("replace()")
    doc_data = jsonable_encoder(doc_in)
    with db_context.bucket.durability(
        persist_to=persist_to, timeout=db_context.config.cb_durability_timeout_secs
    ):
        result = await db_context.bucket.replace(doc_id, doc_data, ttl=ttl)
        if result.success:
            return doc_in
    return None


async def remove(
    db_context: DbContext,
    doc_id: str,
    doc_model: Type[PydanticModel] = None,
    persist_to=0,
) -> Optional[Union[PydanticModel, bool]]:
    logger.debug("remove()")
    result = await db_context.bucket.get(doc_id, quiet=True)
    if not result.value:
        return None
    if doc_model:
        model = doc_model(**result.value)
    with db_context.bucket.durability(
        persist_to=persist_to, timeout=db_context.config.cb_durability_timeout_secs
    ):
        result = await db_context.bucket.remove(doc_id)
        if not result.success:
            return None
        if doc_model:
            return model
        return True


async def run_query(
    db_context: DbContext,
    doc_type: str,
    doc_model: Type[PydanticModel],
    select_fields: List[str],
    where_clause: str = None,
    where_values: List[str] = [],
    order_by: str = None,
    limit: int = None,
):
    logger.debug("run_query()")
    fields = ",".join(select_fields)
    limit_rows = ""
    if limit:
        limit_rows = f"limit {limit}"
    order = ""
    if order_by:
        order = f"order by {order_by}"
    where = ""
    if where_clause:
        where = f"and {where_clause}"
    query = f"select {fields} from {db_context.config.cb_bucket} \
            where type='{doc_type}' {where} {order} {limit_rows}"
    n1ql_query = N1QLQuery(query, *where_values)
    logger.debug(f"n1ql_query: {n1ql_query}")
    results = db_context.bucket.n1ql_query(n1ql_query)
    docs = []
    logger.debug(f"results: {results}")
    async for row in results:
        logger.debug(f"row: {row}")
        doc = doc_model(**row)
        docs.append(doc)
    return docs
