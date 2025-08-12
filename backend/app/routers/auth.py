"""
Authentication routes for login, logout, and OTP operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session
from database import get_session, get_redis
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
from utils.rate_limiter import check_rate_limit
from models.user import User
import redis


router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


# Dependency to rate limit login attempts
async def login_rate_limit(
    request: Request,
    login_data: LoginRequest = Body(...),
    redis_client: redis.Redis = Depends(get_redis),
) -> None:
    check_rate_limit(
        request,
        redis_client,
        5,  # max_attempts
        1,  # window_minutes
        key=f"login:{login_data.email.lower()}",
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
    _: None = Depends(login_rate_limit),
):
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
        3,  # max_attempts
        1,  # window_minutes
        key=f"otp:{otp_data.email.lower()}",
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


@router.get("/me", response_model=UserMeResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> UserMeResponse:
    """Get current user information along with roles and permissions.

    The returned structure contains the user's unique identifier and
    email address, plus a list of role objects (each with id, name,
    display_name and description) and all permissions flattened into
    strings.  This shape matches the frontend `User` type and allows
    the client to determine admin status without additional calls.
    """
    # Compute list of permission strings
    permissions = current_user.get_all_permissions()

    # Build role responses from ORM models.  The RoleResponse pydantic
    # schema expects `display_name` which our Role model does not
    # define; we fall back to using the role name for display_name.
    role_objects = []
    for role in current_user.roles:
        role_dict = {
            "id": role.id,
            "name": role.name,
            # Provide a human‑readable display_name; fallback to name
            "display_name": getattr(
                role, "display_name",
                role.name,
            ),
            "description": role.description,
        }
        role_objects.append(RoleResponse.model_validate(role_dict))

    # Build a full user response dictionary from the ORM object.  The
    # UserResponse schema will extract all standard fields from the
    # SQLModel instance.  We then supply the roles and permissions
    # explicitly when constructing the ``UserMeResponse``.
    user_dict = UserResponse.model_validate(current_user).model_dump()
    return UserMeResponse(
        **user_dict,
        roles=role_objects,
        permissions=permissions,
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
