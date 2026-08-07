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

app = FastAPI(
    title=settings.app_name,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    description="API for processing CSV/Excel files and dynamic filtering.",
    version="0.1.0",
)

# Configuración CORS para permitir peticiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los headers
)

app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name}"}
