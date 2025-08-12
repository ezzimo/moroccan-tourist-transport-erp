"""
Authentication service for login/logout operations (async API, threadpool-backed)
"""

from sqlmodel import Session, select
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from models.user import User
from schemas.auth import LoginRequest, LoginResponse
from schemas.user import UserResponse
from utils.security import (
    verify_token as decode_jwt,
    verify_password,
    create_access_token,
    blacklist_token,
    is_token_blacklisted,
)
from config import settings
from datetime import datetime, timedelta
import redis
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication operations"""

    def __init__(self, session: Session | None, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client

    # -------------------- Public async wrappers --------------------

    async def login(self, login_data: LoginRequest) -> LoginResponse:
        return await run_in_threadpool(self._login_sync, login_data)

    async def logout(self, token: str) -> dict:
        return await run_in_threadpool(self._logout_sync, token)

    async def verify_token(self, token: str) -> User:
        return await run_in_threadpool(self._verify_token_sync, token)

    # -------------------- Internal sync implementations --------------------

    def _login_sync(self, login_data: LoginRequest) -> LoginResponse:
        assert self.session is not None, "DB session required for login"

        logger.info("Login attempt for email=%s", login_data.email)
        statement = select(User).where(User.email == login_data.email)
        user = self.session.exec(statement).first()

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
        self.session.commit()
        self.session.refresh(user)

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

    def _logout_sync(self, token: str) -> dict:
        expires = settings.access_token_expire_minutes * 60
        blacklist_token(token, self.redis, expires_in_seconds=expires)
        logger.info("Logout: token blacklisted")
        return {"message": "Successfully logged out"}

    def _verify_token_sync(self, token: str) -> User:
        assert self.session is not None, "DB session required for verify_token"

        if is_token_blacklisted(token, self.redis):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        token_data = decode_jwt(token)
        logger.debug(
            "Verifying token for user_id=%s", getattr(token_data, "user_id", None)
        )
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        statement = select(User).where(User.id == token_data.user_id)
        user = self.session.exec(statement).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return user
