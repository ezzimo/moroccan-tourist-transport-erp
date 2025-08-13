# utils/rate_limiter.py
from __future__ import annotations
from fastapi import HTTPException, Request, status, Depends, Body
from datetime import timedelta
from typing import Optional, Callable, Any
from database import get_redis  # keep existing sync provider for tests
from utils.redis_compat import r_expire, r_pipeline_incr_ttl

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
    """Redis-backed (sync/async compatible) fixed-window limiter."""

    def __init__(
        self,
        redis_client: Any,
        *,
        key: str,
        max_attempts: int,
        window_seconds: int,
    ):
        self.redis = redis_client
        self.key = key
        self.max_attempts = int(max_attempts)
        self.window = int(window_seconds)

    async def check_or_raise(self) -> None:
        try:
            count, ttl = await r_pipeline_incr_ttl(self.redis, self.key)

            if ttl == -1:
                await r_expire(self.redis, self.key, self.window)
                ttl = self.window

            if count == 1:
                await r_expire(self.redis, self.key, self.window)
                ttl = self.window

            if count > self.max_attempts:
                remaining = (
                    ttl if isinstance(ttl, int) and ttl > 0 else self.window
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        "Rate limit exceeded. Try again in "
                        f"{remaining} seconds."
                    ),
                )
        except HTTPException:
            raise
        except Exception:
            # fail-open on Redis issues
            return


def rate_limit_dependency(
    *,
    max_attempts: int = 5,
    window: timedelta = timedelta(minutes=1),
    identifier: Optional[Callable[[Request], str]] = None,
):
    async def _dep(
        request: Request,
        redis_client: Any = Depends(get_redis),
    ) -> None:
        ident = identifier(request) if identifier else _client_ip(request)
        limiter = RateLimiter(
            redis_client,
            key=f"rl:{ident}",
            max_attempts=max_attempts,
            window_seconds=int(window.total_seconds()) or 60,
        )
        await limiter.check_or_raise()

    return _dep


# Email-scoped limiters for Auth flows (no double-increments)
def login_rate_limit():
    async def _dep(
        request: Request,
        payload: dict = Body(...),  # works with FastAPI to read JSON body here
        redis_client: Any = Depends(get_redis),
    ) -> None:
        email = str(payload.get("email", "")).lower().strip()
        ident = f"login:{email}" if email else _client_ip(request)
        limiter = RateLimiter(
            redis_client, key=f"rl:{ident}", max_attempts=5, window_seconds=60
        )
        await limiter.check_or_raise()

    return _dep


def otp_rate_limit():
    async def _dep(
        request: Request,
        payload: dict = Body(...),
        redis_client: Any = Depends(get_redis),
    ) -> None:
        email = str(payload.get("email", "")).lower().strip()
        ident = f"otp:{email}" if email else _client_ip(request)
        limiter = RateLimiter(
            redis_client, key=f"rl:{ident}", max_attempts=3, window_seconds=60
        )
        await limiter.check_or_raise()

    return _dep
