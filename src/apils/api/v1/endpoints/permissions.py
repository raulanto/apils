from fastapi import APIRouter, Depends, status
from typing import List
from apils.schemas.permission import PermissionResponse, PermissionCreate, PermissionUpdate
from apils.domain.services.permission_service import PermissionService
from apils.dependencies.services import get_permission_service
from apils.schemas.response import ApiResponse
from apils.core.fastapi_users import current_active_user

router = APIRouter(prefix="/permissions", tags=["Permissions"])

@router.get("/", response_model=ApiResponse[List[PermissionResponse]])
async def get_permissions(
    service: PermissionService = Depends(get_permission_service),
    user = Depends(current_active_user)
):
    permissions = await service.get_permissions()
    return ApiResponse(data=permissions, message="Permissions retrieved successfully")

@router.get("/{permission_id}", response_model=ApiResponse[PermissionResponse])
async def get_permission(
    permission_id: str,
    service: PermissionService = Depends(get_permission_service),
    user = Depends(current_active_user)
):
    permission = await service.get_permission_by_id(permission_id)
    return ApiResponse(data=permission, message="Permission retrieved successfully")

@router.post("/", response_model=ApiResponse[PermissionResponse], status_code=status.HTTP_201_CREATED)
async def create_permission(
    data: PermissionCreate,
    service: PermissionService = Depends(get_permission_service),
    user = Depends(current_active_user)
):
    permission = await service.create_permission(data)
    return ApiResponse(data=permission, message="Permission created successfully")

@router.put("/{permission_id}", response_model=ApiResponse[PermissionResponse])
async def update_permission(
    permission_id: str,
    data: PermissionUpdate,
    service: PermissionService = Depends(get_permission_service),
    user = Depends(current_active_user)
):
    permission = await service.update_permission(permission_id, data)
    return ApiResponse(data=permission, message="Permission updated successfully")

@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: str,
    service: PermissionService = Depends(get_permission_service),
    user = Depends(current_active_user)
):
    await service.delete_permission(permission_id)
