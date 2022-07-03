from unittest.mock import Mock, patch
from uuid import UUID

from app.core.api.security.login import service as uut
from tests.core.api.conftest import date_created, token_id
from tests.mock import MIN_IN_YEAR, create_core_config


async def test_login_user():
    pass


@patch(
    "app.core.api.security.token.service.util.get_utc_now",
    Mock(return_value=date_created()),
)
@patch("app.core.api.security.token.service.uuid4", Mock(return_value=UUID(token_id())))
@patch(
    "app.core.api.security.login.service.get_core_config",
    Mock(
        return_value=create_core_config(
            override={"login_token_expire_min": MIN_IN_YEAR * 100}
        )
    ),
)
async def test_generate_login_token(db_context, user, login_token, mocker):
    # mocker.patch("app.core.db.service.get_db_context", Mock(return_value=db_context))
    # expected = AccessToken(access_token=login_token, date_expires=None)
    # actual = await uut.generate_login_token(user=user)
    # assert actual == expected
    pass


def test_get_verified_login_token_data(login_token, token_data):
    actual = uut.get_verified_login_token_data(token=login_token)
    assert actual == token_data
