"""
Async Redis-backed rate limiter (fixed window) + FastAPI dependency
"""

from __future__ import annotations
from fastapi import HTTPException, Request, status, Depends
from datetime import timedelta
from typing import Optional, Callable
from redis.asyncio import Redis
from database_async import get_async_redis

TRUSTED_PROXY_HOPS = 1


def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if parts:
            idx = max(0, len(parts) - 1 - TRUSTED_PROXY_HOPS)
            return parts[idx]
    return request.client.host if request.client else "unknown"


class AsyncRateLimiter:
    def __init__(
        self, redis_client: Redis, *, key: str, max_attempts: int, window_seconds: int
    ):
        self.redis = redis_client
        self.key = key
        self.max_attempts = int(max_attempts)
        self.window = int(window_seconds)

    async def check_or_raise(self) -> None:
        try:
            pipe = self.redis.pipeline(transaction=True)
            pipe.incr(self.key)
            pipe.ttl(self.key)
            count, ttl = await pipe.execute()

            if ttl == -1:
                await self.redis.expire(self.key, self.window)
                ttl = self.window

            if count == 1:
                await self.redis.expire(self.key, self.window)
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
            # Fail-open to avoid hard auth outages if Redis hiccups
            return


def async_rate_limit_dependency(
    *,
    max_attempts: int = 5,
    window: timedelta = timedelta(minutes=1),
    identifier: Optional[Callable[[Request], str]] = None,
):
    async def _dep(
        request: Request,
        redis_client: Redis = Depends(get_async_redis),
    ) -> None:
        ident = identifier(request) if identifier else _client_ip(request)
        limiter = AsyncRateLimiter(
            redis_client,
            key=f"rl:{ident}",
            max_attempts=max_attempts,
            window_seconds=int(window.total_seconds()) or 60,
        )
        await limiter.check_or_raise()

    return _dep
