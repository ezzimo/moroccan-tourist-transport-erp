"""
Tests for authentication functionality
"""
from schemas.auth import LoginRequest
import pytest
from fastapi.testclient import TestClient
from services.user_service import UserService
from schemas.user import UserCreate
from services.auth_service import AuthService


class TestAuthentication:
    """Test class for authentication endpoints"""

    @pytest.mark.asyncio
    async def test_login_success(self, session, redis_client, make_user):
        make_user(email="ok@example.com", password="Secret123!")
        svc = AuthService(session, redis_client)
        resp = await svc.login(
            LoginRequest(
                email="ok@example.com", password="Secret123!"
            )
        )
        assert resp.user.email == "ok@example.com"

    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials"""
        response = client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        })

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_logout_success(
        self,
        client: TestClient,
        session,
        sample_user_data,
    ):
        """Test successful logout"""
        # Create user and login
        user_service = UserService(session)
        user_create = UserCreate(**sample_user_data)
        await user_service.create_user(user_create)

        login_response = client.post("/api/v1/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })

        token = login_response.json()["access_token"]

        # Test logout
        response = client.post("/api/v1/auth/logout", headers={
            "Authorization": f"Bearer {token}"
        })

        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_get_current_user_info(
        self,
        client: TestClient,
        session,
        sample_user_data,
    ):
        """Test getting current user information"""
        # Create user and login
        user_service = UserService(session)
        user_create = UserCreate(**sample_user_data)
        await user_service.create_user(user_create)

        login_response = client.post("/api/v1/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })

        token = login_response.json()["access_token"]

        # Test get user info
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })

        assert response.status_code == 200
        data = response.json()
        assert "permissions" in data
        assert "roles" in data

    def test_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token"""
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalid_token"
        })
        assert response.status_code == 401
