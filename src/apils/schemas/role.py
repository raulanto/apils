from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from apils.schemas.permission import PermissionResponse

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: str
    permissions: List[PermissionResponse] = []

    model_config = ConfigDict(from_attributes=True)
