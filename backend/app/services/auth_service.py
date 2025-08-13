"""
Authentication service with sync/async DB & Redis compatibility
"""

from __future__ import annotations
from sqlmodel import select
from fastapi import HTTPException, status
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
from typing import Any
from utils.db_compat import exec_first, commit, refresh, add
from utils.redis_compat import r_exists

import logging

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, session: Any, redis_client: Any):
        self.session = session
        self.redis = redis_client

    async def login(self, login_data: LoginRequest) -> LoginResponse:
        assert self.session is not None, "DB session required for login"

        logger.info("Login attempt for email=%s", login_data.email)
        user = await exec_first(
            self.session, select(User).where(User.email == login_data.email)
        )

        if (not user) or (not verify_password(login_data.password, user.password_hash)):
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
        await add(self.session, user)
        await commit(self.session)
        await refresh(self.session, user)

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
        expires = settings.access_token_expire_minutes * 60
        # blacklist_token must accept sync or async redis (see utils.security)
        await blacklist_token(token, self.redis, expires_in_seconds=expires)
        logger.info("Logout: token blacklisted")
        return {"message": "Successfully logged out"}

    async def verify_token(self, token: str) -> User:
        assert self.session is not None, "DB session required for verify_token"

        if await is_token_blacklisted(token, self.redis):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )

        token_data = decode_jwt(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        user = await exec_first(
            self.session, select(User).where(User.id == token_data.user_id)
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return user
