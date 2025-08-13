# utils/compat.py
from __future__ import annotations
import inspect
from typing import Any, Callable


async def maybe_await(value: Any) -> Any:
    """Await a value if it is awaitable, otherwise return it as-is."""
    if inspect.isawaitable(value):
        return await value  # type: ignore[misc]
    return value


def get_method(obj: Any, name: str) -> Callable[..., Any]:
    fn = getattr(obj, name)
    if not callable(fn):
        raise AttributeError(f"{obj!r} has no callable {name}")
    return fn
