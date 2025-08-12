from fastapi import HTTPException, Request, status
import redis

TRUSTED_PROXY_HOPS = 1  # set to how many proxies you trust adding XFF


def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if parts:
            idx = max(0, len(parts) - 1 - TRUSTED_PROXY_HOPS)
            return parts[idx]
    return request.client.host if request.client else "unknown"


class RateLimiter:
    """Atomic Redis-backed fixed-window rate limiter."""

    def __init__(
        self,
        redis_client: redis.Redis,
        max_attempts: int,
        window_seconds: int,
        key: str,
    ):
        self.redis = redis_client
        self.max_attempts = int(max_attempts)
        self.window = int(window_seconds)
        self.key = key

    def check_or_raise(self) -> None:
        """
        Increments counter for self.key. Applies TTL on first use.
        Raises HTTP 429 if attempts exceed max_attempts.
        """
        try:
            pipe = self.redis.pipeline()
            pipe.incr(self.key)
            pipe.ttl(self.key)
            count, ttl = pipe.execute()

            # ensure TTL exists
            if ttl == -1 or count == 1:
                self.redis.expire(self.key, self.window)
                ttl = self.window

            if int(count) > self.max_attempts:
                remaining = ttl if isinstance(ttl, int) and ttl > 0 else self.window
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {remaining} seconds.",
                )
        except HTTPException:
            raise
        except Exception:
            # Fail-open on Redis errors to avoid auth lockout if Redis is down.
            return
