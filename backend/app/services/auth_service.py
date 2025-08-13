"""
Authentication service for login/logout operations
"""
from datetime import datetime, timedelta
import logging
import redis
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from models.user import User
from schemas.auth import LoginRequest, LoginResponse
from schemas.user import UserResponse
from utils.security import (
    verify_token as decode_jwt,
    verify_password,
    create_access_token,
    blacklist_token_async,
    is_token_blacklisted_async,
)
from config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication operations"""

    def __init__(self, session: AsyncSession | None, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client

    async def login(self, login_data: LoginRequest) -> LoginResponse:
        """Authenticate user and return JWT token"""
        assert self.session is not None, "DB session required for login"

        logger.info("Login attempt for email=%s", login_data.email)

        stmt = select(User).where(User.email == login_data.email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is disabled",
            )

        user.last_login_at = datetime.utcnow()
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            sub=user.id,
            email=user.email,
            scopes=[],
            expires_delta=expires,
        )
        logger.info("Login success user_id=%s", user.id)

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.model_validate(user),
        )

    async def logout(self, token: str) -> dict:
        """Logout user by blacklisting token (store identifier with TTL)"""
        expires = settings.access_token_expire_minutes * 60
        await blacklist_token_async(token, self.redis, expires_in_seconds=expires)
        logger.info("Logout: token blacklisted")
        return {"message": "Successfully logged out"}

    async def verify_token(self, token: str) -> User:
        """Verify token and return user"""
        assert self.session is not None, "DB session required for verify_token"

        if await is_token_blacklisted_async(token, self.redis):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        token_data = decode_jwt(token)
        logger.debug(
            "Verifying token for user_id=%s", token_data.user_id if token_data else None
        )
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        stmt = select(User).where(User.id == token_data.user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return user
