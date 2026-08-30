from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from apils.domain.entities.role import Permission
from apils.schemas.permission import PermissionCreate, PermissionUpdate
from apils.core.exceptions import DomainError
from typing import List

class PermissionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_permissions(self) -> List[Permission]:
        result = await self.session.execute(
            select(Permission)
            .options(selectinload(Permission.action), selectinload(Permission.resource), selectinload(Permission.group))
        )
        return result.scalars().all()

    async def get_permission_by_id(self, permission_id: str) -> Permission:
        result = await self.session.execute(
            select(Permission)
            .options(selectinload(Permission.action), selectinload(Permission.resource), selectinload(Permission.group))
            .where(Permission.id == permission_id)
        )
        permission = result.scalars().first()
        if not permission:
            raise DomainError(f"Permission {permission_id} not found.")
        return permission

    async def create_permission(self, data: PermissionCreate) -> Permission:
        # Check if exists
        stmt = select(Permission).where(
            Permission.action_id == data.action_id,
            Permission.resource_id == data.resource_id
        )
        existing = await self.session.execute(stmt)
        if existing.scalars().first():
            raise DomainError("Permission for this action and resource already exists.")

        permission = Permission(
            action_id=data.action_id,
            resource_id=data.resource_id,
            group_id=data.group_id if data.group_id else None,
            description=data.description
        )
        self.session.add(permission)
        await self.session.commit()
        await self.session.refresh(permission)
        return await self.get_permission_by_id(permission.id)

    async def update_permission(self, permission_id: str, data: PermissionUpdate) -> Permission:
        permission = await self.get_permission_by_id(permission_id)
        
        has_changes = False
        
        if data.action_id is not None or data.resource_id is not None:
            new_action_id = data.action_id if data.action_id is not None else permission.action_id
            new_resource_id = data.resource_id if data.resource_id is not None else permission.resource_id
            
            # Check collision
            stmt = select(Permission).where(
                Permission.action_id == new_action_id,
                Permission.resource_id == new_resource_id,
                Permission.id != permission_id
            )
            existing = await self.session.execute(stmt)
            if existing.scalars().first():
                raise DomainError("Permission with this action and resource already exists.")
            
            permission.action_id = new_action_id
            permission.resource_id = new_resource_id
            has_changes = True

        if data.group_id is not None:
            permission.group_id = data.group_id if data.group_id else None
            has_changes = True

        if data.description is not None:
            permission.description = data.description
            has_changes = True

        if has_changes:
            await self.session.commit()
            await self.session.refresh(permission)
            
        return await self.get_permission_by_id(permission.id)

    async def delete_permission(self, permission_id: str) -> None:
        permission = await self.get_permission_by_id(permission_id)
        await self.session.delete(permission)
        await self.session.commit()
