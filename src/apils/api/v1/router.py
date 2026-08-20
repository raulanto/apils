from fastapi import APIRouter
from apils.api.v1.endpoints import files
from apils.core.fastapi_users import fastapi_users_app, auth_backend, auth_backend_cookie
from apils.schemas.auth import UserRead, UserCreate, UserUpdate

api_router = APIRouter()

api_router.include_router(
    fastapi_users_app.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

api_router.include_router(
    fastapi_users_app.get_auth_router(auth_backend_cookie),
    prefix="/auth/cookie",
    tags=["auth"],
)
api_router.include_router(
    fastapi_users_app.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
api_router.include_router(
    fastapi_users_app.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

api_router.include_router(files.router)
