"""
Async database & Redis providers
"""

from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import settings
from redis.asyncio import Redis


# Compose async DB URL if a sync one was set (guard for older envs)
def _to_async_url(url: str) -> str:
    # allow already-async URLs
    if url.startswith("postgresql+asyncpg://"):
        return url
    # convert legacy sync DSNs
    return url.replace("postgresql://", "postgresql+asyncpg://")


ASYNC_DB_URL = _to_async_url(settings.database_url)

engine = create_async_engine(
    ASYNC_DB_URL,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Redis (async)
redis_client: Redis = Redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def get_async_redis() -> Redis:
    return redis_client
