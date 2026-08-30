from fastapi import APIRouter, Depends, status
from typing import List
from apils.schemas.role import RoleResponse, RoleCreate, RoleUpdate
from apils.domain.services.role_service import RoleService
from apils.dependencies.services import get_role_service
from apils.schemas.response import ApiResponse
from apils.core.fastapi_users import current_active_user

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("/", response_model=ApiResponse[List[RoleResponse]])
async def get_roles(
    service: RoleService = Depends(get_role_service),
    user = Depends(current_active_user)
):
    roles = await service.get_roles()
    return ApiResponse(data=roles, message="Roles retrieved successfully")

@router.get("/{role_id}", response_model=ApiResponse[RoleResponse])
async def get_role(
    role_id: str,
    service: RoleService = Depends(get_role_service),
    user = Depends(current_active_user)
):
    role = await service.get_role_by_id(role_id)
    return ApiResponse(data=role, message="Role retrieved successfully")

@router.post("/", response_model=ApiResponse[RoleResponse], status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    service: RoleService = Depends(get_role_service),
    user = Depends(current_active_user)
):
    role = await service.create_role(data)
    return ApiResponse(data=role, message="Role created successfully")

@router.put("/{role_id}", response_model=ApiResponse[RoleResponse])
async def update_role(
    role_id: str,
    data: RoleUpdate,
    service: RoleService = Depends(get_role_service),
    user = Depends(current_active_user)
):
    role = await service.update_role(role_id, data)
    return ApiResponse(data=role, message="Role updated successfully")

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: str,
    service: RoleService = Depends(get_role_service),
    user = Depends(current_active_user)
):
    await service.delete_role(role_id)

@router.post("/{role_id}/permissions/{permission_id}", response_model=ApiResponse[RoleResponse])
async def assign_permission_to_role(
    role_id: str,
    permission_id: str,
    service: RoleService = Depends(get_role_service),
    user = Depends(current_active_user)
):
    role = await service.assign_permission_to_role(role_id, permission_id)
    return ApiResponse(data=role, message="Permission assigned to role successfully")

@router.delete("/{role_id}/permissions/{permission_id}", response_model=ApiResponse[RoleResponse])
async def remove_permission_from_role(
    role_id: str,
    permission_id: str,
    service: RoleService = Depends(get_role_service),
    user = Depends(current_active_user)
):
    role = await service.remove_permission_from_role(role_id, permission_id)
    return ApiResponse(data=role, message="Permission removed from role successfully")
