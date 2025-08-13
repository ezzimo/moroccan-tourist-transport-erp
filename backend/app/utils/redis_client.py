# backend/app/utils/redis_client.py
from __future__ import annotations

from typing import AsyncGenerator
from redis.asyncio import Redis
from config import settings


def _redis_url() -> str:
    # Adapt to your settings names
    return getattr(settings, "redis_url", None) or getattr(
        settings, "REDIS_URL", "redis://redis_auth:6379/0"
    )


async def get_async_redis() -> AsyncGenerator[Redis, None]:
    """
    FastAPI dependency that yields a redis.asyncio client.
    Tests can override this dependency with fakeredis.
    """
    client: Redis = Redis.from_url(_redis_url(), decode_responses=True)
    try:
        yield client
    finally:
        # Keep shutdown clean; aclose() is available on
        # redis>=4.5 asyncio client
        try:
            await client.aclose()
        except Exception:
            pass
