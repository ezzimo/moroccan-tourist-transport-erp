# utils/rate_limiter.py
from fastapi import HTTPException, Request, status, Depends
from datetime import timedelta
import redis
from typing import Optional, Callable
from database import get_redis

TRUSTED_PROXY_HOPS = 1  # set to how many proxies you trust adding XFF


def _client_ip(request: Request) -> str:
    # Try X-Forwarded-For if behind a trusted proxy
    xff = request.headers.get("x-forwarded-for")
    if xff:
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if parts:
            idx = max(0, len(parts) - 1 - TRUSTED_PROXY_HOPS)
            return parts[idx]
    # Fallback
    return request.client.host if request.client else "unknown"


class RateLimiter:
    """Atomic Redis-backed rate limiter (fixed window)."""

    def __init__(self, redis_client, max_attempts: int, window_minutes: int, key: str):
        self.redis = redis_client
        self.max_attempts = int(max_attempts)
        self.window = int(window_minutes) * 60  # seconds
        self.key = key

    def check_or_raise(self) -> None:
        """
        Increments a counter for `self.key` and applies an expiry on
        first use of the window. If attempts exceed `self.max_attempts`,
        raises HTTP 429 with a remaining-seconds hint.
        """
        try:
            pipe = self.redis.pipeline()
            pipe.incr(self.key)
            pipe.ttl(self.key)
            count, ttl = pipe.execute()

            # If key exists but has no TTL, enforce our window
            if ttl == -1:
                self.redis.expire(self.key, self.window)
                ttl = self.window

            # If this is the first attempt (new key), set the window
            if count == 1:
                self.redis.expire(self.key, self.window)
                ttl = self.window

            if count > self.max_attempts:
                remaining = ttl if isinstance(ttl, int) and ttl > 0 else self.window
                # Message aligned with tests: must contain
                # "Rate limit exceeded"
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {remaining} seconds.",
                )
        except HTTPException:
            raise
        except Exception:
            # Fail-open on Redis errors so auth/OTP still works if Redis is down
            return

    # Optional helpers (not used by tests but kept functional)
    def is_allowed(self, key: str) -> bool:
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.window)
        count, _ = pipe.execute()
        return int(count) <= self.max_attempts

    def attempts(self, key: str) -> int:
        val = self.redis.get(key)
        return int(val) if val else 0


def rate_limit_dependency(
    *,
    max_attempts: int = 5,
    window: timedelta = timedelta(minutes=1),
    identifier: Optional[Callable[[Request], str]] = None,
):
    """Return a FastAPI dependency enforcing rate limit."""

    def _dep(request: Request, redis_client: redis.Redis = Depends(get_redis)) -> None:
        ident = identifier(request) if identifier else _client_ip(request)
        key = f"rl:{ident}"
        limiter = RateLimiter(
            redis_client=redis_client,
            max_attempts=max_attempts,
            window_minutes=int(window.total_seconds() // 60) or 1,
            key=key,
        )
        if not limiter.is_allowed(key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Rate limit exceeded. "
                    f"{limiter.attempts(key)}/{max_attempts} attempts. "
                    "Try again later."
                ),
            )

    return _dep


def check_rate_limit(request, redis_client, max_attempts, window_minutes, *, key: str):
    """
    Convenience wrapper used by routers.
    Example:
        check_rate_limit(request, redis_client, 5, 1, key=f"login:{email}")
    """
    RateLimiter(redis_client, max_attempts, window_minutes, key).check_or_raise()
