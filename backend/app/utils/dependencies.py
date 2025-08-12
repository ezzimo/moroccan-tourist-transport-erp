from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from database import get_session, get_redis
from models.user import User
from utils.security import verify_token, is_token_blacklisted
from schemas.auth import TokenData
import redis
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    session: Session = Depends(get_session),
    redis_client: redis.Redis = Depends(get_redis),
) -> User:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials

    # Blacklist check
    try:
        if is_token_blacklisted(token, redis_client):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # ---- fallback: also check the raw-token key directly ----
        if redis_client.exists(f"blacklist:raw:{token}"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # --------------------------------------------------------
    except Exception as e:
        # If anything goes wrong checking revocation, fail closed
        logger.debug("Blacklist check failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data: TokenData | None = verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user
    user = session.exec(
        select(User).where(User.id == token_data.user_id)
    ).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ✅ Add this wrapper so routers can depend on an “active” user
async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the authenticated user is active, not locked, and not deleted.
    Return the user if all checks pass, otherwise raise 403.
    """
    if user.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is deleted"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is locked",
        )
    return user


# (Optional) central permission guard if you don’t already have it here.
def require_permission(service: str, action: str, resource: str):
    """
    Dependency factory to enforce a specific permission triple.
    """

    def _dep(
            user: User = Depends(get_current_active_user)
    ) -> None:
        if not user.has_permission(service, action, resource):
            # prefer 403 for “authenticated but not allowed”
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

    return _dep
