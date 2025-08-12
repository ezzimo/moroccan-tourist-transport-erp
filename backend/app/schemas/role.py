"""
Role and Permission-related Pydantic schemas
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
import uuid


class PermissionBase(BaseModel):
    service_name: str
    action: str
    resource: str = "*"


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: Optional[list[uuid.UUID]] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[list[uuid.UUID]] = None


class RoleResponse(RoleBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class RoleWithPermissions(RoleResponse):
    permissions: list[PermissionResponse]
    model_config = ConfigDict(from_attributes=True)