from datetime import datetime, timezone

from factory import Faker, Trait

from app.core.security.auth import AuthToken
from app.core.security.token import RevokedToken

from .base_factory import BaseFactory


class AuthTokenFactory(BaseFactory):
    token_type = "Bearer"
    access_token = Faker("pystr")
    access_token_expires_at = Faker("date_time", tzinfo=timezone.utc)
    refresh_token = Faker("pystr")
    refresh_token_expires_at = Faker("date_time", tzinfo=timezone.utc)

    class Meta:
        model = AuthToken

    class Params:
        jan_01_2020 = Trait(
            token_type="Bearer",
            access_token=(
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                "eyJ0b2tlbl9pZCI6ImFlNzg2OWI4LWRjYzQtNDMzMC04MjIyLTZkNjIzM2ExOWEyMCIsImNsYWltIjoiQUNDRVNTX1RPS0VOIiwiZXhwIjoxNTc3ODQwNDAwLCJzdWIiOiJKb2UiLCJkYXRhIjp7InVzZXJuYW1lIjoiSm9lIiwiZmlyc3RfbmFtZSI6IkpvZSIsImxhc3RfbmFtZSI6IkpvZSIsImVtYWlsIjoiam9lQGV4YW1wbGUuY29tIiwidmVyaWZpZWRfZW1haWwiOm51bGwsInJvbGVzIjpbIlVTRVIiXSwiZGlzYWJsZWQiOmZhbHNlLCJkYXRlX2NyZWF0ZWQiOiIyMDIwLTAxLTAxVDAwOjAwOjAwLjAwMCswMDowMCIsImRhdGVfbW9kaWZpZWQiOiIyMDIwLTAxLTAxVDAwOjAwOjAwLjAwMCswMDowMCIsImxhc3RfbG9naW4iOiIyMDIwLTAxLTAxVDAwOjAwOjAwLjAwMCswMDowMCJ9fQ."  # pylint: disable=line-too-long
                "iXLPwg5cUQupmZ5PYYoblqEzegmv6P-c7ANigePRLoA"
            ),
            access_token_expires_at=datetime(2020, 1, 1, 1, 0, tzinfo=timezone.utc),
            refresh_token=(
                "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                "eyJ0b2tlbl9pZCI6ImM3YmJiNjAzLWU0YzItNGQ0ZS1hMmQwLWVhZTkyNjgzZjE3NiIsImNsYWltIjoiUkVGUkVTSF9UT0tFTiIsImV4cCI6MTU3Nzg0NzYwMCwic3ViIjoiSm9lIiwiZGF0YSI6bnVsbH0."  # pylint: disable=line-too-long
                "5A-So-cGjQ75lC2GGWDsAGOxxcJkgyx1m_-R6xw_704"
            ),
            refresh_token_expires_at=datetime(2020, 1, 1, 3, 0, tzinfo=timezone.utc),
        )


class RevokedTokenFactory(BaseFactory):
    token_id = Faker("pystr")
    claim = Faker("pystr")
    exp = Faker("pyint")
    sub = Faker("pystr")
    data = {"test": "testing"}
    revoke_reason = Faker("pystr")

    class Meta:
        model = RevokedToken
