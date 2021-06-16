import asyncio
import logging
from datetime import datetime
from unittest import TestCase

import pytest
from fastapi.exceptions import HTTPException

from app.core.crud.user import get_user_doc_id
from app.core.db import crud_utils as uut
from app.core.models.user import USER_DOC_TYPE, UserDb, UserUpdateDb
from app.tests.core.db.utils import get_test_user_db
from app.tests.db_utils import clean_up_db, get_db_context
from app.tests.utils import get_test_username

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def teardown_module():
    asyncio.run(clean_up_db())


@pytest.mark.asyncio
async def test_crud():
    now = datetime.now()
    username = get_test_username()
    doc_id = get_user_doc_id(username=username)
    user = get_test_user_db(username=username, now=now)
    db_context = await get_db_context()
    result_insert = await uut.insert(db_context=db_context, doc_id=doc_id, doc_in=user)
    assert result_insert is not None
    TestCase().assertDictEqual(user.dict(), result_insert.dict())
    with pytest.raises(HTTPException):
        duplicate_insert = await uut.insert(
            db_context=db_context, doc_id=doc_id, doc_in=user
        )
    result_get_doc = await uut.get_doc(
        db_context=db_context, doc_id=doc_id, doc_model=UserDb
    )
    assert result_get_doc is not None
    TestCase().assertDictEqual(user.dict(), result_get_doc.dict())
    result_unspecified_doc_model_get_doc = await uut.get_doc(
        db_context=db_context, doc_id=doc_id
    )
    assert result_unspecified_doc_model_get_doc is not None
    assert isinstance(result_unspecified_doc_model_get_doc, dict)
    TestCase().assertDictEqual(
        user.dict(), UserDb(**result_unspecified_doc_model_get_doc).dict()
    )
    result_nonexistant_get_doc = await uut.get_doc(
        db_context=db_context, doc_id=doc_id + "nonexistant_id", doc_model=UserDb
    )
    assert result_nonexistant_get_doc is None
    updated = UserUpdateDb(full_name="updated user")
    expected_update = get_test_user_db(username=username, now=now)
    expected_update.full_name = "updated user"
    result_update = await uut.update(
        db_context=db_context, doc_id=doc_id, doc=user, doc_updated=updated
    )
    assert result_update is not None
    TestCase().assertDictEqual(expected_update.dict(), result_update.dict())
    result_updated_get_doc = await uut.get_doc(
        db_context=db_context, doc_id=doc_id, doc_model=UserDb
    )
    assert result_updated_get_doc is not None
    TestCase().assertDictEqual(expected_update.dict(), result_updated_get_doc.dict())
    result_nonexistant_remove = await uut.remove(
        db_context=db_context, doc_id=doc_id + "nonexistant_id", doc_model=UserDb
    )
    assert result_nonexistant_remove is None
    result_remove = await uut.remove(
        db_context=db_context, doc_id=doc_id, doc_model=UserDb
    )
    assert result_remove is not None
    TestCase().assertDictEqual(expected_update.dict(), result_remove.dict())
    result_after_remove = await uut.get_doc(
        db_context=db_context, doc_id=doc_id, doc_model=UserDb
    )
    assert result_after_remove is None
    await uut.insert(db_context=db_context, doc_id=doc_id, doc_in=user)
    result_unspecified_doc_model_remove = await uut.remove(
        db_context=db_context, doc_id=doc_id
    )
    assert result_unspecified_doc_model_remove is True


@pytest.mark.asyncio
async def test_run_query():
    db_context = await get_db_context()
    username_1 = get_test_username()
    doc_id_1 = get_user_doc_id(username=username_1)
    user_1 = get_test_user_db(username=username_1, now=datetime.now())
    await uut.insert(db_context=db_context, doc_id=doc_id_1, doc_in=user_1)
    username_2 = get_test_username()
    doc_id_2 = get_user_doc_id(username=username_2)
    user_2 = get_test_user_db(username=username_2, now=datetime.now())
    await uut.insert(db_context=db_context, doc_id=doc_id_2, doc_in=user_2)
    username_3 = get_test_username()
    doc_id_3 = get_user_doc_id(username=username_3)
    user_3 = get_test_user_db(username=username_3, now=datetime.now())
    await uut.insert(db_context=db_context, doc_id=doc_id_3, doc_in=user_3)
    results = await uut.run_query(
        db_context=db_context,
        doc_type="nonexistant_type",
        doc_model=UserDb,
    )
    assert len(results) == 0
    results = await uut.run_query(
        db_context=db_context,
        doc_type=USER_DOC_TYPE,
        doc_model=UserDb,
    )
    assert len(results) >= 3
    results = await uut.run_query(
        db_context=db_context, doc_type=USER_DOC_TYPE, doc_model=UserDb, limit=2
    )
    assert len(results) == 2
    results = await uut.run_query(
        db_context=db_context,
        doc_type=USER_DOC_TYPE,
        doc_model=UserDb,
        where_clause="doc->>'username'=$1",
        where_values=[username_1],
    )
    assert len(results) == 1
    assert results[0].username == username_1
    results = await uut.run_query(
        db_context=db_context,
        doc_type=USER_DOC_TYPE,
        doc_model=UserDb,
        order_by="doc->>'date_created' desc",
        where_clause="doc_id in ($1, $2, $3)",
        where_values=[doc_id_1, doc_id_2, doc_id_3],
    )
    assert len(results) == 3
    actual_order = []
    for r in results:
        actual_order.append(r.username)
    TestCase().assertListEqual([username_3, username_2, username_1], actual_order)
    results = await uut.run_query(
        db_context=db_context,
        doc_type=USER_DOC_TYPE,
        doc_model=UserDb,
        order_by="doc->>'date_created' asc",
        where_clause="doc_id in ($1, $2, $3)",
        where_values=[doc_id_1, doc_id_2, doc_id_3],
    )
    assert len(results) == 3
    actual_order = []
    for r in results:
        actual_order.append(r.username)
    TestCase().assertListEqual([username_1, username_2, username_3], actual_order)
