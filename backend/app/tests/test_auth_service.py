# backend/app/tests/test_auth_service.py
"""
Unit tests for the AuthService. These tests exercise
the service logic directly (using the test DB session
and fakeredis from fixtures) and are fast & deterministic.
"""

import pytest
from config import settings
from models.user import User
from schemas.auth import LoginRequest
from services.auth_service import AuthService
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from utils.security import is_token_blacklisted_async
from utils.security import verify_token as decode_jwt


class TestAuthService:
    @pytest.mark.asyncio
    async def test_login_success(
        self, session: AsyncSession, redis_client: Redis, make_user
    ):
        """
        User with correct credentials receives a valid JWT
        and last_login(_at) is set.
        """
        user: User = await make_user(email="ok@example.com", password="Secret123!")

        svc = AuthService(session, redis_client)
        resp = await svc.login(
            LoginRequest(email="ok@example.com", password="Secret123!")
        )

        assert resp.token_type == "bearer"
        assert resp.expires_in == settings.access_token_expire_minutes * 60
        assert resp.user.email == "ok@example.com"

        token_data = decode_jwt(resp.access_token)
        assert token_data is not None
        assert token_data.email == "ok@example.com"
        assert token_data.user_id == user.id

        # last_login is set by the service; last_login_at may also be used.
        await session.refresh(user)
        assert user.last_login_at is not None

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self, session: AsyncSession, redis_client: Redis, make_user
    ):
        """Wrong password returns 401."""
        await make_user(email="fail@example.com", password="RightPass1!")
        svc = AuthService(session, redis_client)

        with pytest.raises(Exception) as exc:
            await svc.login(
                LoginRequest(email="fail@example.com", password="WrongPass1!")
            )
        assert "Incorrect email or password" in str(exc.value)

    @pytest.mark.asyncio
    async def test_login_disabled_user(
        self, session: AsyncSession, redis_client: Redis, make_user
    ):
        """Disabled users cannot log in."""
        await make_user(
            email="disabled@example.com",
            password="Pw12345!!",
            is_active=False,
        )
        svc = AuthService(session, redis_client)

        with pytest.raises(Exception) as exc:
            await svc.login(
                LoginRequest(
                    email="disabled@example.com", password="Pw12345!!"
                )
            )
        assert "User account is disabled" in str(exc.value)

    @pytest.mark.asyncio
    async def test_logout_blacklists_token(
        self, session: AsyncSession, redis_client: Redis, make_user
    ):
        """Logout stores the JTI in Redis; subsequent use should be denied."""
        await make_user(email="logout@example.com", password="PW!2345678")
        svc = AuthService(session, redis_client)

        login_resp = await svc.login(
            LoginRequest(email="logout@example.com", password="PW!2345678")
        )

        out = await svc.logout(login_resp.access_token)
        assert out["message"] == "Successfully logged out"

        assert (
            await is_token_blacklisted_async(
                login_resp.access_token,
                redis_client,
            )
            is True
        )

    @pytest.mark.asyncio
    async def test_verify_token_valid(
        self, session: AsyncSession, redis_client: Redis, make_user
    ):
        """Verify a valid token returns the user."""
        user = await make_user(email="verify@example.com", password="PwOk!!22")
        svc = AuthService(session, redis_client)
        login_resp = await svc.login(
            LoginRequest(email="verify@example.com", password="PwOk!!22")
        )

        u = await svc.verify_token(login_resp.access_token)
        assert u.id == user.id

    @pytest.mark.asyncio
    async def test_verify_token_revoked(
        self, session: AsyncSession, redis_client: Redis, make_user
    ):
        """Revoked token is rejected."""
        await make_user(email="revoked@example.com", password="PwOk!!22")
        svc = AuthService(session, redis_client)
        login_resp = await svc.login(
            LoginRequest(email="revoked@example.com", password="PwOk!!22")
        )
        await svc.logout(login_resp.access_token)

        with pytest.raises(Exception) as exc:
            await svc.verify_token(login_resp.access_token)
        assert "Token has been revoked" in str(exc.value)

    @pytest.mark.asyncio
    async def test_verify_token_invalid(
        self,
        session: AsyncSession,
        redis_client: Redis,
    ):
        """Garbage tokens are rejected."""
        svc = AuthService(session, redis_client)
        with pytest.raises(Exception) as exc:
            await svc.verify_token("not.a.jwt")
        assert "Invalid token" in str(exc.value)
