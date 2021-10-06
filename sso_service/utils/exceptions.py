from typing import Any, Optional
from fastapi import Request
from fastapi.exceptions import StarletteHTTPException, RequestValidationError
from .response import DJSONResponse


class WebException(Exception):

    DEFAULT_ERROR_CODES = {
        400: "KO_BAD_REQUEST",
        401: "KO_AUTH",
        403: "KO_FORBIDDEN",
        404: "KO_NOT_FOUND",
        405: "KO_NOT_ALLOWED",
        409: "KO_CONFLICT",
        410: "KO_GONE",
        422: "KO_UNPROCESSABLE_PAYLOAD",
        500: "ERR_CANT_PERFORM"
    }

    status_code: int = ...
    default_message: str = ...

    def __init__(self, reason: Optional[Any] = None, message: Optional[str] = None, exc_code: Optional[str] = None, is_critical: bool = False):
        self.exc_code = exc_code or self.DEFAULT_ERROR_CODES[self.status_code]
        self.msg = message or self.default_message
        self.reason = reason
        self.is_critical = is_critical


class CantPerform(WebException):
    status_code = 500
    default_message = "Cannot perform operation."


class BadRequest(WebException):
    status_code = 400
    default_message = "Bad request."


class Unauthorized(WebException):
    status_code = 401
    default_message = "Wrong credentials"


class Forbidden(WebException):
    status_code = 403
    default_message = "Permission denied."


class NotFound(WebException):
    status_code = 404
    default_message = "Resource not found."


class NotAllowed(WebException):
    status_code = 405
    default_message = "Method not allowed."


class Conflict(WebException):
    status_code = 409
    default_message = "Conflict with current state."


class Gone(WebException):
    status_code = 410
    default_message = "Access to the resource is no longer available."


class NotValid(WebException):
    status_code = 422
    default_message = "Sended data is not valid"


class ExceptionResponse(WebException):
    status_code = 0
    default_message = "An error has occurred."

    def __init__(self, status_code: int, reason: Optional[Any] = None, message: Optional[str] = None, 
    exc_code: Optional[str] = None, is_critical: bool = False):
        self.status_code = status_code
        super().__init__(reason=reason, message=message, exc_code=exc_code, is_critical=is_critical)


# Main exception handlers

async def web_exception_handler(_: Request, exc: WebException):
    return DJSONResponse(
        content=exc.reason, 
        status_code=exc.status_code,
        body_meta_code=exc.exc_code, 
        body_meta_extra={"is_critical": exc.is_critical}, 
        body_meta_message=str(exc.msg)
    )


async def starlette_http_exception_handler(_: Request, exc: StarletteHTTPException):
    return DJSONResponse(
        content=str(exc.detail), 
        status_code=exc.status_code, 
        body_meta_code=WebException.DEFAULT_ERROR_CODES[exc.status_code], 
        body_meta_message="Error"
    )


async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return DJSONResponse(
        content=str(exc), 
        status_code=422, 
        body_meta_code=WebException.DEFAULT_ERROR_CODES[422], 
        body_meta_message="Validation Error"
    )