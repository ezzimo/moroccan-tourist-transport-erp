# backend/app/utils/dependencies.py
from __future__ import annotations

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from redis.asyncio import Redis
import logging

from utils.db import get_async_session
from utils.redis_client import get_async_redis  # keep your actual provider path
from utils.security import verify_token, is_token_blacklisted_async  # async blacklist helper
from utils.redis_compat import r_exists  # compat layer (awaitable)
from schemas.auth import TokenData
from models.user import User

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    session: AsyncSession = Depends(get_async_session),
    redis_client: Redis = Depends(get_async_redis),
) -> User:
    """
    Resolve the current user from the Authorization: Bearer token.
    Works fully async with AsyncSession and redis.asyncio client.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials

    # Blacklist checks (async, non-blocking)
    try:
        if await is_token_blacklisted_async(token, redis_client):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # raw-token fallback key
        if await r_exists(redis_client, f"blacklist:raw:{token}"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        logger.debug("Blacklist check failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode JWT (sync; tiny CPU work)
    token_data: TokenData | None = verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user via AsyncSession (this replaces the old .exec(...))
    result = await session.execute(
        select(User).where(User.id == token_data.user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """
    Ensure the resolved user is active.
    """
    if not getattr(user, "is_active", True):
        # You may prefer 400 or 403—tests usually accept 401/403 patterns;
        # keep consistent with your previous behavior.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user


def require_permission(service: str, action: str, resource: str):
    async def _dep(
        user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_async_session),
    ) -> None:
        result = await session.execute(select(User).where(User.id == user.id))
        db_user = result.scalar_one_or_none()
        if not db_user or not db_user.has_permission(service, action, resource):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
    return _dep
