from datetime import datetime
from typing import Any

from pydantic import BaseModel


class Event(BaseModel):
    name: str
    payload: Any = None
    date_created: datetime = datetime.now()
