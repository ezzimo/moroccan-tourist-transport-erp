"""
Test database configuration and session management
"""
from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
import fakeredis.aioredis

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite+aiosqlite://"

# Create an async engine for the test database
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create a session maker for the test engine
TestSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Fake Redis client for testing
test_redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)


async def create_test_db_and_tables():
    """Create database tables"""
    from models.user import User, UserRole  # noqa: F401
    from models.role import Role, RolePermission  # noqa: F401
    from models.permission import Permission  # noqa: F401
    from models.activity_log import ActivityLog  # noqa: F401
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_test_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Test database session dependency"""
    async with TestSessionLocal() as session:
        yield session


def get_test_redis() -> fakeredis.aioredis.FakeRedis:
    """Test Redis client dependency"""
    return test_redis_client
