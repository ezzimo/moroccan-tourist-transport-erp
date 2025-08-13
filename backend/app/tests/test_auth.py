"""
Tests for authentication functionality
"""
import pytest
from httpx import AsyncClient
from services.auth_service import AuthService
from schemas.auth import LoginRequest
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from schemas.user import UserCreate


class TestAuthentication:
    """Test class for authentication endpoints"""

    @pytest.mark.asyncio
    async def test_login_success(self, session: AsyncSession, redis_client: Redis, make_user):
        await make_user(email="ok@example.com", password="Secret123!")
        svc = AuthService(session, redis_client)
        resp = await svc.login(
            LoginRequest(
                email="ok@example.com", password="Secret123!"
            )
        )
        assert resp.user.email == "ok@example.com"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials"""
        response = await client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        })

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_logout_success(
        self,
        client: AsyncClient,
        sample_user_data,
        make_user,
        auth_header
    ):
        """Test successful logout"""
        # Create user and login
        await make_user(**sample_user_data)
        headers = await auth_header(sample_user_data["email"], sample_user_data["password"])

        # Test logout
        response = await client.post("/api/v1/auth/logout", headers=headers)

        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_get_current_user_info(
        self,
        client: AsyncClient,
        sample_user_data,
        make_user,
        auth_header,
    ):
        """Test getting current user information"""
        # Create user and login
        await make_user(**sample_user_data)
        headers = await auth_header(sample_user_data["email"], sample_user_data["password"])

        # Test get user info
        response = await client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "permissions" in data
        assert "roles" in data

    @pytest.mark.asyncio
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Test accessing protected endpoint without token"""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_protected_endpoint_with_invalid_token(self, client: AsyncClient):
        """Test accessing protected endpoint with invalid token"""
        response = await client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalid_token"
        })
        assert response.status_code == 401
