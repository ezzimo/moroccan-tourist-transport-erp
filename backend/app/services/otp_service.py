"""
OTP service for one-time password operations
"""

import random
import string
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from config import settings
import redis
import json


class OTPService:
    """Service for handling OTP operations"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def generate_otp(self) -> str:
        """Generate a 6-digit OTP"""
        return "".join(random.choices(string.digits, k=6))

    async def send_otp(self, email: str, purpose: str = "verification") -> dict:
        """Send OTP to user (mocked implementation)"""
        # Check if there's an active OTP
        otp_key = f"otp:{email}:{purpose}"
        existing_otp = self.redis.get(otp_key)

        if existing_otp:
            data = json.loads(existing_otp)
            if data.get("attempts", 0) >= settings.otp_max_attempts:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Maximum OTP attempts exceeded. Please try again later.",
                )

        # Generate new OTP
        otp_code = self.generate_otp()
        otp_data = {
            "code": otp_code,
            "email": email,
            "purpose": purpose,
            "created_at": datetime.utcnow().isoformat(),
            "attempts": 0,
        }

        # Store OTP in Redis with expiration
        self.redis.setex(
            otp_key, settings.otp_expire_minutes * 60, json.dumps(otp_data)
        )

        # Mock SMS/Email sending
        await self._mock_send_otp(email, otp_code, purpose)

        return {
            "message": f"OTP sent to {email}",
            "expires_in": settings.otp_expire_minutes * 60,
        }

    async def verify_otp(
        self, email: str, otp_code: str, purpose: str = "verification"
    ) -> bool:
        """Verify OTP code"""
        otp_key = f"otp:{email}:{purpose}"
        otp_data_str = self.redis.get(otp_key)

        if not otp_data_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP not found or expired",
            )

        otp_data = json.loads(otp_data_str)

        # Check attempts
        if otp_data.get("attempts", 0) >= settings.otp_max_attempts:
            self.redis.delete(otp_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Maximum OTP attempts exceeded",
            )

        # Increment attempts
        otp_data["attempts"] += 1
        self.redis.setex(
            otp_key, settings.otp_expire_minutes * 60, json.dumps(otp_data)
        )

        # Verify code
        if otp_data["code"] != otp_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code"
            )

        # Delete OTP after successful verification
        self.redis.delete(otp_key)
        return True

    async def _mock_send_otp(self, email: str, otp_code: str, purpose: str):
        """Mock OTP delivery via SMS/Email"""
        print(f"[MOCK OTP] Sending OTP to {email}")
        print(f"[MOCK OTP] Code: {otp_code}")
        print(f"[MOCK OTP] Purpose: {purpose}")
        print(f"[MOCK OTP] Expires in: {settings.otp_expire_minutes} minutes")

        # In production, integrate with:
        # - SMS provider (e.g., Twilio, AWS SNS)
        # - Email service (e.g., SendGrid, AWS SES)
        # For Morocco: consider local SMS gateways
