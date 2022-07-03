from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from pydantic import SecretStr

from app.core.db.model import ResourceAlreadyExistsException, ResourceNotFoundException
from app.core.user import crud as uut
from app.core.user.model import UserCreate, UserDb, UserUpdate, UserUpdatePrivate
from tests.mock import create_user_dict, doc_row_user, mock_connection_factory


@pytest.fixture
def username():
    return "tester"


@pytest.fixture
def user_db():
    return UserDb(**create_user_dict())


@pytest.fixture
def user_update(user_update_dict):
    return UserUpdate(**user_update_dict)


@pytest.fixture
def user_update_private(user_update_private_dict):
    return UserUpdatePrivate(**user_update_private_dict)


def test_get_user_doc_id(username):
    actual = uut.get_user_doc_id(username)
    assert actual == "USER::tester"


@pytest.mark.expected_data(doc_row_user())
async def test_get_user_found(db_context, user_db):
    actual = await uut.get_user(db_context=db_context, username=user_db.username)
    assert actual == user_db


async def test_get_user_not_found(db_context, username):
    actual = await uut.get_user(db_context=db_context, username=username)
    assert actual == None


@pytest.mark.expected_data([doc_row_user()])
async def test_get_user_by_email_found(db_context, user_db):
    actual = await uut.get_user_by_email(
        db_context=db_context, email="tester@example.com"
    )
    assert actual == user_db


async def test_get_user_by_email_not_found(db_context):
    actual = await uut.get_user_by_email(
        db_context=db_context, email="tester@example.com"
    )
    assert actual == None


@patch(
    "app.core.user.crud.datetime",
    Mock(now=Mock(return_value=datetime(2020, 1, 1, 0, 0))),
)
@patch("app.core.user.crud.crypt", Mock(hash_password=Mock(return_value="hashed")))
async def test_create_user_success(db_context, user_db):
    user_create = UserCreate(
        **user_db.dict(), password=SecretStr("pass"), password_match=SecretStr("pass")
    )
    actual = await uut.create_user(db_context=db_context, user_create=user_create)
    assert actual == user_db


@pytest.mark.expected_data([doc_row_user()])
async def test_create_user_resource_already_exists(db_context, user_db):
    user_create = UserCreate(
        **user_db.dict(), password=SecretStr("pass"), password_match=SecretStr("pass")
    )
    with pytest.raises(
        ResourceAlreadyExistsException,
        match=f"An account already exists with this email",
    ):
        await uut.create_user(db_context=db_context, user_create=user_create)


async def test_validate_email_update_valid(db_context):
    update_email = "update@example.com"
    current_email = "current@example.com"
    actual = await uut.validate_email_update(
        db_context=db_context, update_email=update_email, current_email=current_email
    )
    assert actual is True


@pytest.mark.expected_data([doc_row_user()])
async def test_validate_email_update_already_exists(db_context):
    update_email = "tester@example.com"
    current_email = "current@example.com"
    with pytest.raises(
        ResourceAlreadyExistsException,
        match=f"An account already exists with email {update_email}",
    ):
        await uut.validate_email_update(
            db_context=db_context,
            update_email=update_email,
            current_email=current_email,
        )


async def test_validate_email_update_no_update_email(db_context):
    update_email = None
    current_email = "current@example.com"
    actual = await uut.validate_email_update(
        db_context=db_context, update_email=update_email, current_email=current_email
    )
    assert actual is None


async def test_validate_email_update_same_email(db_context):
    update_email = "current@example.com"
    current_email = "current@example.com"
    actual = await uut.validate_email_update(
        db_context=db_context, update_email=update_email, current_email=current_email
    )
    assert actual is None


@patch(
    "app.core.user.crud.datetime",
    Mock(now=Mock(return_value=datetime(2022, 2, 2, 0, 0))),
)
@patch(
    "app.core.user.crud.crypt", Mock(hash_password=Mock(return_value="hashed_update"))
)
@pytest.mark.expected_data(multi_expected=[doc_row_user(), None])
async def test_update_user_update_all(
    db_context, user_update, username, updated_user_dict
):
    expected = updated_user_dict

    actual = await uut.update_user(
        db_context=db_context, user_update=user_update, username=username
    )

    assert actual.dict() == expected


@patch(
    "app.core.user.crud.datetime",
    Mock(now=Mock(return_value=datetime(2022, 2, 2, 0, 0))),
)
@pytest.mark.expected_data(multi_expected=[doc_row_user(), None])
async def test_update_user_not_password(
    db_context, user_update, username, user_db, updated_user_dict
):
    expected = updated_user_dict
    expected["password_hash"] = user_db.password_hash

    user_update.password = None

    actual = await uut.update_user(
        db_context=db_context, user_update=user_update, username=username
    )

    assert actual.dict() == expected


@patch(
    "app.core.user.crud.datetime",
    Mock(now=Mock(return_value=datetime(2022, 2, 2, 0, 0))),
)
async def test_update_user_optional_fields(
    db_context, username, user_db, user_update_dict
):
    user_update_dict.pop("password")
    user_update_dict.pop("password_match")

    for key in user_update_dict:
        expected = user_db.dict()
        expected["date_modified"] = datetime(2022, 2, 2, 0, 0)
        expected[key] = user_update_dict[key]

        just_one = {}
        just_one[key] = user_update_dict[key]
        user_update = UserUpdate(**just_one)
        db_context.connection = mock_connection_factory(
            multi_expected=[doc_row_user(), None]
        )
        actual = await uut.update_user(
            db_context=db_context, user_update=user_update, username=username
        )
        assert actual.dict() == expected


async def test_update_user_not_found(db_context, user_update, username):
    with pytest.raises(ResourceNotFoundException, match=f"User not found"):
        await uut.update_user(
            db_context=db_context, username=username, user_update=user_update
        )


@pytest.mark.expected_data(
    multi_expected=[
        doc_row_user(),
        [doc_row_user({"username": "another_tester"})],
    ]
)
async def test_update_user_email_already_exists(db_context, user_update, username):
    with pytest.raises(
        ResourceAlreadyExistsException,
        match=f"An account already exists with email {user_update.email}",
    ):
        await uut.update_user(
            db_context=db_context, username=username, user_update=user_update
        )


@pytest.mark.expected_data(doc_row_user())
async def test_update_user_private_update_all(
    db_context, user_update_private, username, updated_user_private_dict
):
    actual = await uut.update_user_private(
        db_context=db_context,
        user_update_private=user_update_private,
        username=username,
    )

    assert actual.dict() == updated_user_private_dict


@pytest.mark.expected_data(doc_row_user())
async def test_update_user_private_optional_fields(
    db_context, username, user_db, user_update_private_dict
):
    for key in user_update_private_dict:
        expected = user_db.dict()
        expected[key] = user_update_private_dict[key]

        just_one = {}
        just_one[key] = user_update_private_dict[key]
        user_update_private = UserUpdatePrivate(**just_one)

        actual = await uut.update_user_private(
            db_context=db_context,
            user_update_private=user_update_private,
            username=username,
        )

        assert actual.dict() == expected


async def test_update_user_private_not_found(db_context, user_update_private, username):
    with pytest.raises(ResourceNotFoundException, match=f"User not found"):
        await uut.update_user_private(
            db_context=db_context,
            username=username,
            user_update_private=user_update_private,
        )
