from fastapi import APIRouter, Depends
from typing import List
from apils.schemas.auth import UserRead
from apils.domain.services.user_service import UserService
from apils.dependencies.services import get_user_service
from apils.schemas.response import ApiResponse
from apils.core.fastapi_users import current_active_user

router = APIRouter(prefix="/users-list", tags=["users"])

@router.get("/", response_model=ApiResponse[List[UserRead]])
async def get_users(
    service: UserService = Depends(get_user_service),
    user = Depends(current_active_user)
):
    users = await service.get_users()
    return ApiResponse(data=users, message="Users retrieved successfully")
