from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class Meta(BaseModel):
    page: int | None = None
    page_size: int | None = None
    total: int | None = None

class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: str | None = None
    meta: Meta | None = None

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict] | None = None

class ApiError(BaseModel):
    success: bool = False
    error: ErrorDetail
