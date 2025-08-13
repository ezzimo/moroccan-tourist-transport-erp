# utils/db_compat.py
from __future__ import annotations
from typing import Any
from sqlmodel import SQLModel
from sqlmodel.sql.expression import Select
from utils.compat import maybe_await, get_method


async def exec_first(session: Any, stmt: Select) -> Any:
    """
    session may be sync (SQLModel Session) or
    async (SQLModel AsyncSession).
    """
    # SQLModel's AsyncSession has .exec() that returns awaitable result
    exec_fn = get_method(session, "exec")
    res = await maybe_await(exec_fn(stmt))
    # res is a ScalarResult/Result, first() is sync
    return res.first()


async def exec_all(session: Any, stmt: Select) -> list[Any]:
    exec_fn = get_method(session, "exec")
    res = await maybe_await(exec_fn(stmt))
    return list(res.all())


async def commit(session: Any) -> None:
    commit_fn = get_method(session, "commit")
    await maybe_await(commit_fn())


async def refresh(session: Any, instance: SQLModel) -> None:
    refresh_fn = get_method(session, "refresh")
    await maybe_await(refresh_fn(instance))


async def add(session: Any, instance: SQLModel) -> None:
    add_fn = get_method(session, "add")
    # add() is sync on both, but keep maybe_await for safety
    await maybe_await(add_fn(instance))


async def delete(session: Any, instance: SQLModel) -> None:
    delete_fn = get_method(session, "delete")
    await maybe_await(delete_fn(instance))
