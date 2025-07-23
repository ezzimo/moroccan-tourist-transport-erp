"""
Authentication routes for login, logout, and OTP operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session
from database import get_session, get_redis
from services.auth_service import AuthService
from services.otp_service import OTPService
from schemas.auth import (
    LoginRequest, LoginResponse, OTPRequest, OTPVerifyRequest, PermissionsResponse
)
from utils.dependencies import get_current_active_user
from utils.rate_limiter import check_rate_limit
from models.user import User
import redis


router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Authenticate user and return JWT token"""
    # Rate limiting for login attempts
    check_rate_limit(
        request, 
        redis_client, 
        max_attempts=5, 
        window_minutes=1,
        identifier_func=lambda req: f"login:{login_data.email}"
    )
    
    auth_service = AuthService(session, redis_client)
    return await auth_service.login(login_data)


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Logout user by blacklisting token"""
    auth_service = AuthService(None, redis_client)
    return await auth_service.logout(credentials.credentials)


@router.post("/send-otp")
async def send_otp(
    request: Request,
    otp_data: OTPRequest,
    redis_client: redis.Redis = Depends(get_redis)
):
    """Send OTP to user's email/phone"""
    # Rate limiting for OTP requests
    check_rate_limit(
        request,
        redis_client,
        max_attempts=3,
        window_minutes=1,
        identifier_func=lambda req: f"otp:{otp_data.email}"
    )
    
    otp_service = OTPService(redis_client)
    return await otp_service.send_otp(otp_data.email)


@router.post("/verify-otp")
async def verify_otp(
    otp_data: OTPVerifyRequest,
    redis_client: redis.Redis = Depends(get_redis)
):
    """Verify OTP code"""
    otp_service = OTPService(redis_client)
    success = await otp_service.verify_otp(otp_data.email, otp_data.otp_code)
    
    if success:
        return {"message": "OTP verified successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )


@router.get("/me", response_model=PermissionsResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information and permissions"""
    permissions = current_user.get_all_permissions()
    roles = [role.name for role in current_user.roles]
    
    return PermissionsResponse(
        permissions=permissions,
        roles=roles
    )


@router.get("/permissions", response_model=PermissionsResponse)
async def get_user_permissions(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's permissions and roles"""
    permissions = current_user.get_all_permissions()
    roles = [role.name for role in current_user.roles]
    
    return PermissionsResponse(
        permissions=permissions,
        roles=roles
    )