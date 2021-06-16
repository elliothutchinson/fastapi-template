from datetime import datetime

from app.core.models.user import UserDb
from app.tests.utils import TEST_EMAIL_SUFFIX


def get_test_user_db(username: str, now: datetime):
    return UserDb(
        username=username,
        full_name="test user",
        email=f"{username}{TEST_EMAIL_SUFFIX}",
        disabled=False,
        verified=False,
        date_created=now,
        date_modified=now,
        last_login=now,
        hashed_password="hashed password",
    )
