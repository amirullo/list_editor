
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import BaseAPIException
from app.utils.logger import logger

async def api_exception_handler(request: Request, exc: BaseAPIException):
    """
    Handles exceptions of type BaseAPIException and its subclasses, returning a
    standardized JSON response.
    """
    logger.error(f"API Exception caught: {exc.__class__.__name__} - {exc.detail}",
                 extra={"status_code": exc.status_code, "detail": exc.detail})
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}, # Changed 'detail' to 'message'
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handles all other exceptions, returning a generic 500 Internal Server Error
    response to avoid exposing internal details.
    """
    logger.error(f"An unexpected error occurred: {exc.__class__.__name__} - {str(exc)}",
                 exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred."}, # Changed 'detail' to 'message'
    )
