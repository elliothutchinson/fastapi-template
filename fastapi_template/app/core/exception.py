from fastapi import HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)

from app.core.config import core_config

# todo: generalize into non http exception and add handler for converting to http exception

not_found_exception = HTTPException(
    status_code=HTTP_404_NOT_FOUND, detail="Resource not found"
)

credentials_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": core_config.token_type},
)


def get_already_exists_exception(detail: str):
    return HTTPException(status_code=HTTP_409_CONFLICT, detail=detail)


def get_bad_request_exception(detail: str):
    return HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=detail)
