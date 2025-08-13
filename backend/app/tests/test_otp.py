"""
Tests for OTP functionality
"""
from httpx import AsyncClient
import json
import pytest
from redis.asyncio import Redis
from datetime import datetime, timezone, timedelta


class TestOTP:
    """Test class for OTP endpoints"""

    @pytest.mark.asyncio
    async def test_send_otp_success(self, client: AsyncClient):
        """Test successful OTP sending"""
        response = await client.post("/api/v1/auth/send-otp", json={
            "email": "test@example.com"
        })

        assert response.status_code == 200
        data = response.json()
        assert "OTP sent to" in data["message"]
        assert "expires_in" in data

    @pytest.mark.asyncio
    async def test_verify_otp_success(self, client: AsyncClient, redis_client: Redis):
        """Test successful OTP verification"""
        email = "test@example.com"
        otp_code = "123456"

        # Manually set OTP in Redis for testing
        otp_data = {
            "code": otp_code,
            "email": email,
            "purpose": "verification",
            "attempts": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await redis_client.setex(
            f"otp:{email}:verification", 300, json.dumps(otp_data)
        )

        # Test OTP verification
        response = await client.post("/api/v1/auth/verify-otp", json={
            "email": email,
            "otp_code": otp_code
        })

        assert response.status_code == 200
        assert "OTP verified successfully" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_verify_otp_invalid_code(self, client: AsyncClient, redis_client: Redis):
        """Test OTP verification with invalid code"""
        email = "test@example.com"

        # Set OTP in Redis
        otp_data = {
            "code": "123456",
            "email": email,
            "purpose": "verification",
            "attempts": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await redis_client.setex(
            f"otp:{email}:verification", 300, json.dumps(otp_data)
        )

        # Test with wrong code
        response = await client.post("/api/v1/auth/verify-otp", json={
            "email": email,
            "otp_code": "wrong_code"
        })

        assert response.status_code == 400
        assert "Invalid OTP code" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_verify_otp_expired(self, client: AsyncClient, redis_client: Redis):
        """Test OTP verification with expired code"""
        email = "test@example.com"
        otp_code = "123456"

        # Manually set OTP in Redis for testing
        otp_data = {
            "code": otp_code,
            "email": email,
            "purpose": "verification",
            "attempts": 0,
            "created_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
        }
        await redis_client.setex(
            f"otp:{email}:verification", 300, json.dumps(otp_data)
        )

        response = await client.post("/api/v1/auth/verify-otp", json={
            "email": "test@example.com",
            "otp_code": "123456"
        })

        assert response.status_code == 400
        assert "OTP has expired" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_otp_rate_limiting(self, client: AsyncClient):
        """Test OTP rate limiting"""
        email_data = {"email": "test@example.com"}

        # Send multiple OTP requests to trigger rate limiting
        for _ in range(4):  # Max is 3 per minute
            await client.post("/api/v1/auth/send-otp", json=email_data)

        # This should be rate limited
        response = await client.post("/api/v1/auth/send-otp", json=email_data)
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]
