from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from typing import AsyncGenerator

from config import settings

# Expect settings to expose an async URL, e.g. "postgresql+asyncpg://..."
ASYNC_DATABASE_URL = getattr(settings, "database_url_async", None) or getattr(
    settings, "DATABASE_URL_ASYNC", None
)
if not ASYNC_DATABASE_URL:
    # Fall back to a single source if your settings uses `database_url`
    ASYNC_DATABASE_URL = settings.database_url  # must already be async-dialect

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    future=True,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an AsyncSession.
    Tests can override this dependency with a fixture/transactional session.
    """
    async with SessionLocal() as session:
        yield session
