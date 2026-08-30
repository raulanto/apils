from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from apils.infrastructure.database import get_db

from apils.domain.services.file_service import FileService
from apils.domain.services.report_service import ReportService
from apils.domain.services.role_service import RoleService
from apils.domain.services.permission_service import PermissionService
from apils.domain.services.user_service import UserService

def get_file_service() -> FileService:
    return FileService()

def get_report_service() -> ReportService:
    return ReportService(file_service=get_file_service())

def get_role_service(session: AsyncSession = Depends(get_db)) -> RoleService:
    return RoleService(session)

def get_permission_service(session: AsyncSession = Depends(get_db)) -> PermissionService:
    return PermissionService(session)

def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)
