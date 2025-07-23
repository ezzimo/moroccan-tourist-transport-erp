"""
Role and Permission-related Pydantic schemas
"""
from pydantic import BaseModel
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


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: Optional[List[uuid.UUID]] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[uuid.UUID]] = None


class RoleResponse(RoleBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]


class RoleWithPermissions(RoleResponse):
    permissions: List[PermissionResponse]