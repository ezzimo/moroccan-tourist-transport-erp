"""
Authentication-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr
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


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str


class PermissionsResponse(BaseModel):
    permissions: List[str]
    roles: List[str]


# Import here to avoid circular imports
from .user import UserResponse
LoginResponse.model_rebuild()