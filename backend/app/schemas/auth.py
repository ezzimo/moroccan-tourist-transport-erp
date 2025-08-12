"""
Authentication-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import uuid


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: "UserResponse"


class TokenData(BaseModel):
    user_id: Optional[uuid.UUID] = None
    email: Optional[str] = None
    exp: Optional[int] = None
    jti: Optional[str] = None
    scopes: list[str] = Field(default_factory=list)


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str


class PermissionsResponse(BaseModel):
    permissions: list[str]
    roles: list[str]


# Import here to avoid circular imports
from .user import UserResponse, RoleResponse
LoginResponse.model_rebuild()

# Added response model for the current authenticated users.  When calling
# `/auth/me` we want to return the user’s identifier and email along
# with their role objects and computed permission strings.  Returning
# the full user record with permissions in a single call makes it
# straightforward for the frontend AuthContext to populate roles and
# permissions without needing to reconcile disparate structures.


class UserMeResponse(UserResponse):
    """Schema returned by the `/auth/me` endpoint.

    Extends the base ``UserResponse`` with the roles and permissions
    lists.  ``UserResponse`` already includes all of the standard
    user fields (id, full_name, email, phone, status flags, etc.).
    ``roles`` is a list of ``RoleResponse`` objects and ``permissions``
    is a list of permission strings.  This shape aligns with the
    frontend ``User`` type used in the AuthContext.
    """
    roles: list[RoleResponse]
    permissions: list[str]