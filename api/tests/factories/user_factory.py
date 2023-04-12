from datetime import datetime, timezone
from uuid import uuid4

from factory import Faker, LazyAttribute, Trait
from faker import Faker as OrigFaker
from pydantic import SecretStr

from app.core.user.model import (
    UserCreate,
    UserPrivate,
    UserPublic,
    UserUpdate,
    UserUpdatePrivate,
)
from app.core.user.repo import UserDb
from tests import util

from .base_factory import BaseDbFactory, BaseFactory


class UserPublicFactory(BaseFactory):
    username = LazyAttribute(lambda o: f"{OrigFaker().user_name()}_{str(uuid4())}")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = LazyAttribute(lambda o: f"{o.username}@example.com".lower())
    verified_email = None
    roles = ["USER"]
    disabled = False
    date_created = Faker("date_time", tzinfo=timezone.utc)
    date_modified = Faker("date_time", tzinfo=timezone.utc)
    last_login = Faker("date_time", tzinfo=timezone.utc)

    class Meta:
        model = UserPublic

    class Params:
        created = Trait(date_modified=None, last_login=None)
        verified = Trait(verified_email=LazyAttribute(lambda o: o.email))
        joe = Trait(
            username="Joe",
            first_name="Joe",
            last_name="Joe",
            date_created=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
            date_modified=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
            last_login=datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc),
        )


class UserPrivateFactory(UserPublicFactory):
    password_hash = util.password_hash()

    class Meta:
        model = UserPrivate


class UserDbFactory(UserPrivateFactory, BaseDbFactory):
    class Meta:
        model = UserDb


class UserUpdateFactory(BaseFactory):
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    email = LazyAttribute(
        lambda o: f"{OrigFaker().user_name()}_{str(uuid4())}@example.com".lower()
    )
    password = SecretStr("password")
    password_match = LazyAttribute(lambda o: o.password)

    class Meta:
        model = UserUpdate


class UserCreateFactory(UserUpdateFactory):
    username = LazyAttribute(lambda o: f"{OrigFaker().user_name()}_{str(uuid4())}")

    class Meta:
        model = UserCreate


class UserUpdatePrivateFactory(BaseFactory):
    verified_email = LazyAttribute(
        lambda o: f"{OrigFaker().user_name()}_{str(uuid4())}@example.com".lower()
    )
    roles = ["ADMIN", "USER"]
    disabled = True
    last_login = Faker("date_time", tzinfo=timezone.utc)

    class Meta:
        model = UserUpdatePrivate
