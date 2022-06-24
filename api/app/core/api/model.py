from pydantic import BaseModel


class ServerResponse(BaseModel):
    message: str