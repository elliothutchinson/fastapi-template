import pytest
from asyncpg.exceptions import UniqueViolationError
from pydantic import BaseModel

from app.core.db import crud as uut
from app.core.db.model import ResourceAlreadyExistsException
from tests.mock import doc_row


def doc_dict():
    return {
        "name": "test",
        "value": "test value",
    }


class DocModel(BaseModel):
    name: str
    value: str = "default value"


@pytest.fixture
def doc_model():
    return DocModel(**doc_dict())


@pytest.mark.expected_data(doc_row(doc_dict()))
async def test_get_doc_found(db_context, doc_model):
    actual = await uut.get_doc(
        db_context=db_context, doc_id="test_id", doc_model=DocModel
    )
    assert actual == doc_model


@pytest.mark.expected_data(None)
async def test_get_doc_not_found(db_context):
    actual = await uut.get_doc(
        db_context=db_context, doc_id="test_id", doc_model=DocModel
    )
    assert actual == None


async def test_create_doc_success(db_context, doc_model):
    actual = await uut.create_doc(
        db_context=db_context, doc_id="test_id", doc=doc_model
    )
    assert actual == doc_model


@pytest.mark.expected_data(None, UniqueViolationError("test exception"))
async def test_create_doc_resource_already_exists(db_context, doc_model):
    doc_id = "test_id"

    with pytest.raises(
        ResourceAlreadyExistsException,
        match=f"Resource with doc_id '{doc_id}' already exists",
    ):
        await uut.create_doc(db_context=db_context, doc_id=doc_id, doc=doc_model)


async def test_update_doc_success(db_context, doc_model):
    doc_updated = DocModel(name="updated_name")
    expected = {"name": "updated_name", "value": "test value"}
    actual = await uut.update_doc(
        db_context=db_context, doc_id="test_id", doc=doc_model, doc_updated=doc_updated
    )
    assert actual.dict() == expected


@pytest.mark.expected_data(doc_row(doc_dict()))
async def test_remove_doc_success(db_context, doc_model):
    actual = await uut.remove_doc(
        db_context=db_context, doc_id="test_id", doc_model=DocModel
    )
    assert actual == doc_model


@pytest.mark.expected_data(None)
async def test_remove_doc_not_found(db_context):
    actual = await uut.remove_doc(
        db_context=db_context, doc_id="test_id", doc_model=DocModel
    )
    assert actual == None


def test_build_query_basic(db_context):
    doc_type = "test"
    expected = f"""
            select doc from {db_context.config.db_table}
            where doc->>'type'='{doc_type}'    
            """
    actual = uut.build_query(db_context=db_context, doc_type=doc_type)
    assert actual == expected


def test_build_query_where_clause(db_context):
    doc_type = "test"
    where_clause = "doc->>'value'=$1"
    expected = f"""
            select doc from {db_context.config.db_table}
            where doc->>'type'='{doc_type}' and {where_clause}   
            """
    actual = uut.build_query(
        db_context=db_context, doc_type=doc_type, where_clause=where_clause
    )
    assert actual == expected


def test_build_query_order_by(db_context):
    doc_type = "test"
    order_by = "value"
    expected = f"""
            select doc from {db_context.config.db_table}
            where doc->>'type'='{doc_type}'  order by {order_by}  
            """
    actual = uut.build_query(
        db_context=db_context, doc_type=doc_type, order_by=order_by
    )
    assert actual == expected


def test_build_query_limit(db_context):
    doc_type = "test"
    limit = 5
    expected = f"""
            select doc from {db_context.config.db_table}
            where doc->>'type'='{doc_type}'   limit {limit} 
            """
    actual = uut.build_query(db_context=db_context, doc_type=doc_type, limit=limit)
    assert actual == expected


def test_build_query_offset(db_context):
    doc_type = "test"
    offset = 5
    expected = f"""
            select doc from {db_context.config.db_table}
            where doc->>'type'='{doc_type}'    offset {offset}
            """
    actual = uut.build_query(db_context=db_context, doc_type=doc_type, offset=offset)
    assert actual == expected


def test_build_query_where_clause_order_by_limit_offset(db_context):
    doc_type = "test"
    where_clause = "doc->>'value'=$1"
    order_by = "value"
    limit = 5
    offset = 5
    expected = f"""
            select doc from {db_context.config.db_table}
            where doc->>'type'='{doc_type}' and {where_clause} order by {order_by} limit {limit} offset {offset}
            """
    actual = uut.build_query(
        db_context=db_context,
        doc_type=doc_type,
        where_clause=where_clause,
        order_by=order_by,
        limit=limit,
        offset=offset,
    )
    assert actual == expected


@pytest.mark.expected_data([doc_row(doc_dict())])
async def test_query_doc_found(db_context, doc_model):
    actual = await uut.query_doc(
        db_context=db_context, doc_type="test", doc_model=DocModel
    )
    assert len(actual) == 1
    assert actual[0] == doc_model


@pytest.mark.expected_data([])
async def test_query_doc_not_found_empty(db_context):
    actual = await uut.query_doc(
        db_context=db_context, doc_type="test", doc_model=DocModel
    )
    assert len(actual) == 0


async def test_query_doc_not_found_none(db_context):
    actual = await uut.query_doc(
        db_context=db_context, doc_type="test", doc_model=DocModel
    )
    assert len(actual) == 0
