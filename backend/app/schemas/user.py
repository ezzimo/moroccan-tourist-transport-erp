from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, Any
from datetime import datetime
import uuid


class UserBase(BaseModel):
    """Base user schema"""
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=1, max_length=20)


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8)
    role_ids: Optional[list[uuid.UUID]] = None
    is_verified: Optional[bool] = False
    must_change_password: Optional[bool] = False
    avatar_url: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=1, max_length=20)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_locked: Optional[bool] = None
    must_change_password: Optional[bool] = None
    avatar_url: Optional[str] = None
    role_ids: Optional[list[uuid.UUID]] = None


class UserResponse(UserBase):
    """Schema for user response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    is_locked: bool
    must_change_password: bool
    avatar_url: Optional[str] = None
    failed_login_attempts: int
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


def to_display_name(name: str) -> str:
    return name.replace("_", " ").title()


class RoleResponse(BaseModel):
    """Schema for role response"""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None

    @field_validator("display_name", mode="before")
    @classmethod
    def derive_display_name(cls, v, info):
        if v is not None:
            return v
        name = info.data.get("name")
        return to_display_name(name) if name else None


class UserWithRoles(UserResponse):
    """Schema for user with roles"""
    roles: list[RoleResponse] = Field(default_factory=list)


class BulkUserUpdate(BaseModel):
    """Schema for bulk user updates"""
    user_ids: list[uuid.UUID] = Field(..., min_length=1)
    status_updates: dict[str, Any] = Field(..., min_length=1)


class UserSearchRequest(BaseModel):
    """Schema for user search request"""
    search: Optional[str] = None
    role_ids: Optional[list[uuid.UUID]] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_locked: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    last_login_after: Optional[datetime] = None
    last_login_before: Optional[datetime] = None
    include_deleted: bool = False
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    sort_by: str = "created_at"
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


class UserActivityResponse(BaseModel):
    """Schema for user activity response"""
    id: str
    action: str
    resource: str
    description: str
    actor_email: str
    target_user_email: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    created_at: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    new_password: Optional[str] = None


class RoleAssignmentRequest(BaseModel):
    """Schema for role assignment request"""
    role_ids: list[uuid.UUID] = Field(..., min_length=0)


class UserStatusUpdate(BaseModel):
    """Schema for user status update"""
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None
    is_verified: Optional[bool] = None
    must_change_password: Optional[bool] = None


class UserImportResult(BaseModel):
    """Schema for user import result"""
    message: str
    created_count: int
    error_count: int
    errors: list[str] = Field(default_factory=list)


class UserExportRequest(BaseModel):
    """Schema for user export request"""
    format: str = Field("csv", pattern="^(csv|json)$")
    include_deleted: bool = False
    filters: Optional[UserSearchRequest] = None
