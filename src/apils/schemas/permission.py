from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class ActionBase(BaseModel):
    name: str
    description: Optional[str] = None

class ActionCreate(ActionBase):
    pass

class ActionResponse(ActionBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class ResourceBase(BaseModel):
    name: str
    description: Optional[str] = None

class ResourceCreate(ResourceBase):
    pass

class ResourceResponse(ResourceBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class PermissionGroupBase(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionGroupCreate(PermissionGroupBase):
    pass

class PermissionGroupResponse(PermissionGroupBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

class PermissionBase(BaseModel):
    action_id: str
    resource_id: str
    group_id: Optional[str] = None
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    action_id: Optional[str] = None
    resource_id: Optional[str] = None
    group_id: Optional[str] = None
    description: Optional[str] = None

class PermissionResponse(PermissionBase):
    id: str
    name: Optional[str] = None
    action: Optional[ActionResponse] = None
    resource: Optional[ResourceResponse] = None
    group: Optional[PermissionGroupResponse] = None

    model_config = ConfigDict(from_attributes=True)
