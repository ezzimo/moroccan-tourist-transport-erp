"""
Async database & Redis providers
"""

from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import sessionmaker
from config import settings
from redis.asyncio import Redis

_engine = None
_redis_client = None

async_engine = create_async_engine(
    settings.database_url_async,
    echo=False,
    future=True,
)

async_session_maker = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


def get_async_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url_async,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=300,
        )
    return _engine


def get_redis_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
    return _redis_client


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    engine = get_async_engine()
    SessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with SessionLocal() as session:
        yield session


async def get_async_redis() -> Redis:
    return get_redis_client()


async def init_models() -> None:
    engine = get_async_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
