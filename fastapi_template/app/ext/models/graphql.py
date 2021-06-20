from typing import Any

from pydantic import BaseModel


class SecureGraphql(BaseModel):
    user: Any
    error: Any
