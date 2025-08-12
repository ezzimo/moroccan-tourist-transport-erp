"""
OTP service for one-time password operations (async API, threadpool-backed)
"""

import random
import string
from datetime import datetime
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from config import settings
import redis
import json


class OTPService:
    """Service for handling OTP operations"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    # Public async wrappers
    async def send_otp(self, email: str, purpose: str = "verification") -> dict:
        return await run_in_threadpool(self._send_otp_sync, email, purpose)

    async def verify_otp(
        self, email: str, otp_code: str, purpose: str = "verification"
    ) -> bool:
        return await run_in_threadpool(self._verify_otp_sync, email, otp_code, purpose)

    # Internal sync
    def _generate_otp_sync(self) -> str:
        return "".join(random.choices(string.digits, k=6))

    def _send_otp_sync(self, email: str, purpose: str = "verification") -> dict:
        otp_key = f"otp:{email}:{purpose}"
        existing_otp = self.redis.get(otp_key)

        if existing_otp:
            data = json.loads(existing_otp)
            if data.get("attempts", 0) >= settings.otp_max_attempts:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Maximum OTP attempts exceeded. Please try again later.",
                )

        otp_code = self._generate_otp_sync()
        otp_data = {
            "code": otp_code,
            "email": email,
            "purpose": purpose,
            "created_at": datetime.utcnow().isoformat(),
            "attempts": 0,
        }

        self.redis.setex(
            otp_key, settings.otp_expire_minutes * 60, json.dumps(otp_data)
        )

        # MOCK delivery
        print(
            f"[MOCK OTP] Sending OTP to {email} | Code: {otp_code} | Purpose: {purpose}"
        )

        return {
            "message": f"OTP sent to {email}",
            "expires_in": settings.otp_expire_minutes * 60,
        }

    def _verify_otp_sync(
        self, email: str, otp_code: str, purpose: str = "verification"
    ) -> bool:
        otp_key = f"otp:{email}:{purpose}"
        otp_data_str = self.redis.get(otp_key)

        if not otp_data_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP not found or expired",
            )

        otp_data = json.loads(otp_data_str)
        if otp_data.get("attempts", 0) >= settings.otp_max_attempts:
            self.redis.delete(otp_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Maximum OTP attempts exceeded",
            )

        otp_data["attempts"] += 1
        self.redis.setex(
            otp_key, settings.otp_expire_minutes * 60, json.dumps(otp_data)
        )

        if otp_data["code"] != otp_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP code",
            )

        self.redis.delete(otp_key)
        return True
