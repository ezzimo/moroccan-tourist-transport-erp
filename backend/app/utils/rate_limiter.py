from fastapi import HTTPException, Request, status, Depends
from datetime import timedelta
import redis
from typing import Optional, Callable
from database import get_redis

TRUSTED_PROXY_HOPS = 1


def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if parts:
            idx = max(0, len(parts) - 1 - TRUSTED_PROXY_HOPS)
            return parts[idx]
    return request.client.host if request.client else "unknown"


class RateLimiter:
    """Atomic Redis-backed rate limiter (fixed window)."""

    def __init__(self, redis_client, max_attempts: int, window_minutes: int, key: str):
        self.redis = redis_client
        self.max_attempts = int(max_attempts)
        self.window = int(window_minutes) * 60
        self.key = key

    def check_or_raise(self) -> None:
        try:
            pipe = self.redis.pipeline()
            pipe.incr(self.key)
            pipe.ttl(self.key)
            count, ttl = pipe.execute()

            if ttl == -1:
                self.redis.expire(self.key, self.window)
                ttl = self.window
            if count == 1:
                self.redis.expire(self.key, self.window)
                ttl = self.window

            if count > self.max_attempts:
                remaining = ttl if isinstance(ttl, int) and ttl > 0 else self.window
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {remaining} seconds.",
                )
        except HTTPException:
            raise
        except Exception:
            return


# Generic callsite helper (kept for compatibility)
def check_rate_limit(request, redis_client, max_attempts, window_minutes, *, key: str):
    RateLimiter(redis_client, max_attempts, window_minutes, key).check_or_raise()


# ------------- Centralized dependencies (no Body params) -------------
async def login_rate_limit(
    request: Request,
    redis_client: redis.Redis = Depends(get_redis),
) -> None:
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    email = str(payload.get("email", "")).lower()
    key = f"login:{email}" if email else f"login-ip:{_client_ip(request)}"
    RateLimiter(redis_client, 5, 1, key).check_or_raise()


async def otp_rate_limit(
    request: Request,
    redis_client: redis.Redis = Depends(get_redis),
) -> None:
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    email = str(payload.get("email", "")).lower()
    key = f"otp:{email}" if email else f"otp-ip:{_client_ip(request)}"
    RateLimiter(redis_client, 3, 1, key).check_or_raise()
