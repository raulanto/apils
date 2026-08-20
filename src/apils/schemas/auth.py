from pydantic import BaseModel, EmailStr, Field
from fastapi_users import schemas

class UserRead(schemas.BaseUser[str]):
    id: str = Field(description="UUID interno del usuario.")
    email: EmailStr
    is_active: bool = Field(description="Si es False, el usuario no puede iniciar sesión.")
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        from_attributes = True

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass

