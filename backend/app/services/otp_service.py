"""
OTP service with sync/async Redis compatibility
"""

from __future__ import annotations
import random, string, json
from datetime import datetime
from fastapi import HTTPException, status
from config import settings
from typing import Any
from utils.redis_compat import r_get, r_setex, r_del


class OTPService:
    def __init__(self, redis_client: Any):
        self.redis = redis_client

    def generate_otp(self) -> str:
        return "".join(random.choices(string.digits, k=6))

    async def send_otp(self, email: str, purpose: str = "verification") -> dict:
        otp_key = f"otp:{email}:{purpose}"
        existing = await r_get(self.redis, otp_key)

        if existing:
            data = json.loads(existing)
            if data.get("attempts", 0) >= settings.otp_max_attempts:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Maximum OTP attempts exceeded. Please try again later.",
                )

        code = self.generate_otp()
        payload = {
            "code": code,
            "email": email,
            "purpose": purpose,
            "created_at": datetime.utcnow().isoformat(),
            "attempts": 0,
        }
        await r_setex(
            self.redis, otp_key, settings.otp_expire_minutes * 60, json.dumps(payload)
        )
        await self._mock_send_otp(email, code, purpose)
        return {
            "message": f"OTP sent to {email}",
            "expires_in": settings.otp_expire_minutes * 60,
        }

    async def verify_otp(
        self, email: str, otp_code: str, purpose: str = "verification"
    ) -> bool:
        otp_key = f"otp:{email}:{purpose}"
        data = await r_get(self.redis, otp_key)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP not found or expired",
            )

        otp = json.loads(data)
        attempts = int(otp.get("attempts", 0)) + 1
        otp["attempts"] = attempts

        # Keep same TTL window; re-set value with remaining time (simple approach: reset full TTL)
        await r_setex(
            self.redis, otp_key, settings.otp_expire_minutes * 60, json.dumps(otp)
        )

        if otp["code"] != otp_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code"
            )

        await r_del(self.redis, otp_key)
        return True

    async def _mock_send_otp(self, email: str, otp_code: str, purpose: str):
        print(f"[MOCK OTP] Sending OTP to {email}")
        print(f"[MOCK OTP] Code: {otp_code}")
        print(f"[MOCK OTP] Purpose: {purpose}")
        print(f"[MOCK OTP] Expires in: {settings.otp_expire_minutes} minutes")
