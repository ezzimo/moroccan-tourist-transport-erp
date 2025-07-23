"""
User-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str


class UserCreate(UserBase):
    password: str
    role_ids: Optional[List[uuid.UUID]] = []


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    role_ids: Optional[List[uuid.UUID]] = None


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]


class UserWithRoles(UserResponse):
    roles: List["RoleResponse"]


# Import here to avoid circular imports
from .role import RoleResponse
UserWithRoles.model_rebuild()