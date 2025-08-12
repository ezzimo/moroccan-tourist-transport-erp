"""
Tests for OTP functionality
"""
from fastapi.testclient import TestClient
import json


class TestOTP:
    """Test class for OTP endpoints"""

    def test_send_otp_success(self, client: TestClient):
        """Test successful OTP sending"""
        response = client.post("/api/v1/auth/send-otp", json={
            "email": "test@example.com"
        })

        assert response.status_code == 200
        data = response.json()
        assert "OTP sent to" in data["message"]
        assert "expires_in" in data

    def test_verify_otp_success(self, client: TestClient, redis_client):
        """Test successful OTP verification"""
        email = "test@example.com"
        otp_code = "123456"

        # Manually set OTP in Redis for testing
        otp_data = {
            "code": otp_code,
            "email": email,
            "purpose": "verification",
            "attempts": 0
        }
        redis_client.setex(
            f"otp:{email}:verification", 300, json.dumps(otp_data)
        )

        # Test OTP verification
        response = client.post("/api/v1/auth/verify-otp", json={
            "email": email,
            "otp_code": otp_code
        })

        assert response.status_code == 200
        assert "OTP verified successfully" in response.json()["message"]

    def test_verify_otp_invalid_code(self, client: TestClient, redis_client):
        """Test OTP verification with invalid code"""
        email = "test@example.com"

        # Set OTP in Redis
        otp_data = {
            "code": "123456",
            "email": email,
            "purpose": "verification",
            "attempts": 0
        }
        redis_client.setex(
            f"otp:{email}:verification", 300, json.dumps(otp_data)
        )

        # Test with wrong code
        response = client.post("/api/v1/auth/verify-otp", json={
            "email": email,
            "otp_code": "wrong_code"
        })

        assert response.status_code == 400
        assert "Invalid OTP code" in response.json()["detail"]

    def test_verify_otp_expired(self, client: TestClient):
        """Test OTP verification with expired code"""
        response = client.post("/api/v1/auth/verify-otp", json={
            "email": "test@example.com",
            "otp_code": "123456"
        })

        assert response.status_code == 400
        assert "OTP not found or expired" in response.json()["detail"]

    def test_otp_rate_limiting(self, client: TestClient):
        """Test OTP rate limiting"""
        email_data = {"email": "test@example.com"}

        # Send multiple OTP requests to trigger rate limiting
        for _ in range(4):  # Max is 3 per minute
            client.post("/api/v1/auth/send-otp", json=email_data)

        # This should be rate limited
        response = client.post("/api/v1/auth/send-otp", json=email_data)
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]
