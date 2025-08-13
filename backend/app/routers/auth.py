"""
Authentication routes for login, logout, and OTP operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from database_async import get_async_session, get_async_redis
from services.auth_service import AuthService
from services.otp_service import OTPService
from schemas.auth import (
    LoginRequest,
    LoginResponse,
    OTPRequest,
    OTPVerifyRequest,
    PermissionsResponse,
    UserMeResponse,
)
from schemas.user import RoleResponse, UserResponse
from utils.dependencies import get_current_active_user
from utils.rate_limiter import login_rate_limit, otp_rate_limit
from models.user import User
from redis.asyncio import Redis

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_async_redis),
    _: None = Depends(login_rate_limit),
):
    auth_service = AuthService(session, redis_client)
    return await auth_service.login(login_data)


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis_client: Redis = Depends(get_async_redis),
):
    """Logout user by blacklisting token"""
    auth_service = AuthService(None, redis_client)
    return await auth_service.logout(credentials.credentials)


@router.post("/send-otp")
async def send_otp(
    request: Request,
    otp_data: OTPRequest,
    redis_client: Redis = Depends(get_async_redis),
    _: None = Depends(otp_rate_limit),
):
    """Send OTP to user's email/phone"""
    otp_service = OTPService(redis_client)
    return await otp_service.send_otp(otp_data.email)


@router.post("/verify-otp")
async def verify_otp(
    otp_data: OTPVerifyRequest,
    redis_client: Redis = Depends(get_async_redis),
):
    """Verify OTP code"""
    otp_service = OTPService(redis_client)
    success = await otp_service.verify_otp(otp_data.email, otp_data.otp_code)
    if success:
        return {"message": "OTP verified successfully"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")


@router.get("/me", response_model=UserMeResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> UserMeResponse:
    permissions = current_user.get_all_permissions()
    role_objects = []
    for role in current_user.roles:
        role_dict = {
            "id": role.id,
            "name": role.name,
            "display_name": getattr(role, "display_name", role.name),
            "description": role.description,
        }
        role_objects.append(RoleResponse.model_validate(role_dict))

    user_dict = UserResponse.model_validate(current_user).model_dump()
    return UserMeResponse(**user_dict, roles=role_objects, permissions=permissions)


@router.get("/permissions", response_model=PermissionsResponse)
async def get_user_permissions(current_user: User = Depends(get_current_active_user)):
    permissions = current_user.get_all_permissions()
    roles = [role.name for role in current_user.roles]
    return PermissionsResponse(permissions=permissions, roles=roles)
