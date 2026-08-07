from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from apils.core.exceptions import DomainError
from apils.schemas.response import ApiError, ErrorDetail

logger = logging.getLogger(__name__)

async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiError(
            error=ErrorDetail(code=exc.code, message=exc.message, details=exc.details)
        ).model_dump(),
    )

async def validation_error_handler(request: Request, exc: RequestValidationError):
    details = [{"field": ".".join(str(x) for x in e["loc"]), "msg": e["msg"]} for e in exc.errors()]
    return JSONResponse(
        status_code=422,
        content=ApiError(
            error=ErrorDetail(code="VALIDATION_ERROR", message="Error de validación", details=details)
        ).model_dump(),
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ApiError(
            error=ErrorDetail(code="INTERNAL_ERROR", message="Error interno del servidor")
        ).model_dump(),
    )
