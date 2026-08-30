from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from apils.domain.entities.role import Role, Permission
from apils.schemas.role import RoleCreate, RoleUpdate
from apils.core.exceptions import DomainError
from typing import List

class RoleService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_roles(self) -> List[Role]:
        # Include permissions in the result
        stmt = select(Role).options(
            selectinload(Role.permissions).selectinload(Permission.action),
            selectinload(Role.permissions).selectinload(Permission.resource),
            selectinload(Role.permissions).selectinload(Permission.group)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_role_by_id(self, role_id: str) -> Role:
        stmt = (
            select(Role)
            .options(
                selectinload(Role.permissions).selectinload(Permission.action),
                selectinload(Role.permissions).selectinload(Permission.resource),
                selectinload(Role.permissions).selectinload(Permission.group)
            )
            .where(Role.id == role_id)
        )
        result = await self.session.execute(stmt)
        role = result.scalars().first()
        if not role:
            raise DomainError(f"Role {role_id} not found.")
        return role

    async def create_role(self, data: RoleCreate) -> Role:
        # Check if exists
        stmt = select(Role).where(Role.name == data.name)
        existing = await self.session.execute(stmt)
        if existing.scalars().first():
            raise DomainError(f"Role with name {data.name} already exists.")

        role = Role(name=data.name, description=data.description)
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        
        # Load relationships explicitly after refresh to avoid DetachedInstanceError
        return await self.get_role_by_id(role.id)

    async def update_role(self, role_id: str, data: RoleUpdate) -> Role:
        role = await self.get_role_by_id(role_id)
        
        if data.name is not None:
            # Check name collision
            stmt = select(Role).where(Role.name == data.name, Role.id != role_id)
            existing = await self.session.execute(stmt)
            if existing.scalars().first():
                raise DomainError(f"Role with name {data.name} already exists.")
            role.name = data.name

        if data.description is not None:
            role.description = data.description

        await self.session.commit()
        await self.session.refresh(role)
        return await self.get_role_by_id(role.id)

    async def delete_role(self, role_id: str) -> None:
        role = await self.get_role_by_id(role_id)
        await self.session.delete(role)
        await self.session.commit()

    async def assign_permission_to_role(self, role_id: str, permission_id: str) -> Role:
        role = await self.get_role_by_id(role_id)
        
        permission = await self.session.get(Permission, permission_id)
        if not permission:
            raise DomainError(f"Permission {permission_id} not found.")

        # Check if already assigned
        if any(p.id == permission_id for p in role.permissions):
            raise DomainError(f"Permission {permission_id} is already assigned to role {role_id}.")

        role.permissions.append(permission)
        await self.session.commit()
        await self.session.refresh(role)
        return await self.get_role_by_id(role.id)

    async def remove_permission_from_role(self, role_id: str, permission_id: str) -> Role:
        role = await self.get_role_by_id(role_id)
        
        # Find permission in role
        permission_to_remove = next((p for p in role.permissions if p.id == permission_id), None)
        
        if not permission_to_remove:
            raise DomainError(f"Permission {permission_id} is not assigned to role {role_id}.")

        role.permissions.remove(permission_to_remove)
        await self.session.commit()
        await self.session.refresh(role)
        return await self.get_role_by_id(role.id)
