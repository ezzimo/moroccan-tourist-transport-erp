# utils/redis_compat.py
from __future__ import annotations
from typing import Any, Tuple
from utils.compat import maybe_await, get_method


async def r_get(client: Any, key: str) -> Any:
    return await maybe_await(get_method(client, "get")(key))


async def r_setex(client: Any, key: str, ttl_seconds: int, value: str) -> Any:
    return await maybe_await(
        get_method(client, "setex")(
            key,
            ttl_seconds,
            value,
        )
    )


async def r_incr(client: Any, key: str) -> int:
    return int(await maybe_await(get_method(client, "incr")(key)))


async def r_ttl(client: Any, key: str) -> int:
    return int(await maybe_await(get_method(client, "ttl")(key)))


async def r_expire(client: Any, key: str, ttl_seconds: int) -> Any:
    return await maybe_await(get_method(client, "expire")(key, ttl_seconds))


async def r_exists(client: Any, key: str) -> bool:
    val = await maybe_await(get_method(client, "exists")(key))
    # redis-py returns int; fakeredis may return bool
    return bool(val)


async def r_del(client: Any, key: str) -> Any:
    return await maybe_await(get_method(client, "delete")(key))


async def r_pipeline_incr_ttl(client: Any, key: str) -> Tuple[int, int]:
    """
    Portable 'pipeline': try real pipeline if available,
    otherwise do two calls.
    Returns (count, ttl)
    """
    pipe_attr = getattr(client, "pipeline", None)
    if pipe_attr is None:
        # fallback: not truly atomic but good enough for tests
        count = await r_incr(client, key)
        ttl = await r_ttl(client, key)
        return count, ttl

    pipe = pipe_attr()
    enter = getattr(pipe, "__aenter__", None)
    exit_ = getattr(pipe, "__aexit__", None)

    if callable(enter) and callable(exit_):
        # async pipeline
        async with pipe:
            await maybe_await(get_method(pipe, "incr")(key))
            await maybe_await(get_method(pipe, "ttl")(key))
            res = await maybe_await(get_method(pipe, "execute")())
        count, ttl = res
        return int(count), int(ttl)

    # sync pipeline
    pipe.incr(key)
    pipe.ttl(key)
    res = pipe.execute()
    count, ttl = res
    return int(count), int(ttl)
