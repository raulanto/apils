from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from apils.core.config import settings
from apils.api.v1.router import api_router
from apils.core.exceptions import DomainError
from apils.core.exception_handlers import (
    domain_error_handler,
    validation_error_handler,
    unhandled_exception_handler,
)

from fastapi.middleware.cors import CORSMiddleware
from apils.api.middlewares.logging import LoggingMiddleware

app = FastAPI(
    title=settings.app_name,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    description="API for processing CSV/Excel files and dynamic filtering.",
    version="0.1.0",
)

# Configuración CORS estricta (usando FRONTEND_CORS_ORIGINS desde el .env)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # o especificar: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name}"}
