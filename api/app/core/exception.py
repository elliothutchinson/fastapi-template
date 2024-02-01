from typing import Callable, Type

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.core.api.model import ServerResponse


class ResourceNotFoundException(Exception):
    pass


class DataConflictException(Exception):
    pass


class InvalidTokenException(Exception):
    pass


class InvalidCredentialException(Exception):
    pass


class UserDisabedException(Exception):
    pass


def _exception_mapping() -> dict:
    return {
        DataConflictException: 409,
        ResourceNotFoundException: 404,
        UserDisabedException: 403,
        InvalidCredentialException: 401,
        InvalidTokenException: 401,
    }


def _handler_factory(code: int) -> Callable:
    async def handler(_request: Request, exc: Type[Exception]) -> JSONResponse:
        response = ServerResponse(message=str(exc))

        return JSONResponse(status_code=code, content=response.dict())

    return handler


def _http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    response = ServerResponse(message=exc.detail)

    return JSONResponse(status_code=exc.status_code, content=response.dict())


def register_exceptions(app: FastAPI):
    exceptions = _exception_mapping()

    for exception, status_code in exceptions.items():
        app.exception_handler(exception)(_handler_factory(status_code))

    app.exception_handler(HTTPException)(_http_exception_handler)


# todo: handle framework exceptions to use same serverresponse msg response
