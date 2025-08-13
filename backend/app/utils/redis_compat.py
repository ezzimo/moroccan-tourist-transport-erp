# utils/redis_compat.py
from __future__ import annotations
from typing import Any, Tuple
from redis.asyncio import Redis


async def r_get(client: Redis, key: str) -> Any:
    return await client.get(key)


async def r_setex(client: Redis, key: str, ttl_seconds: int, value: str) -> None:
    await client.setex(key, ttl_seconds, value)


async def r_incr(client: Redis, key: str) -> int:
    return await client.incr(key)


async def r_ttl(client: Redis, key: str) -> int:
    return await client.ttl(key)


async def r_expire(client: Redis, key: str, ttl_seconds: int) -> Any:
    return await client.expire(key, ttl_seconds)


async def r_exists(client: Redis, key: str) -> bool:
    return await client.exists(key)


async def r_del(client: Redis, key: str) -> Any:
    return await client.delete(key)


async def r_pipeline_incr_ttl(client: Redis, key: str) -> Tuple[int, int]:
    """
    Portable 'pipeline': try real pipeline if available,
    otherwise do two calls.
    Returns (count, ttl)
    """
    async with client.pipeline() as pipe:
        await pipe.incr(key)
        await pipe.ttl(key)
        count, ttl = await pipe.execute()
    return int(count), int(ttl)
