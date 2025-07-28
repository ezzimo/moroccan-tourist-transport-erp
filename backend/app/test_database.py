"""
Test database configuration and session management
"""
from sqlmodel import SQLModel, create_engine, Session
from test_config import test_settings
import fakeredis
from typing import Generator


# SQLite engine for testing
test_engine = create_engine(
    test_settings.database_url,
    echo=test_settings.debug,
    connect_args={"check_same_thread": False}
)

# Fake Redis client for testing
test_redis_client = fakeredis.FakeRedis(decode_responses=True)


def create_test_db_and_tables():
    """Create test database tables"""
    SQLModel.metadata.create_all(test_engine)


def get_test_session() -> Generator[Session, None, None]:
    """Test database session dependency"""
    with Session(test_engine) as session:
        yield session


def get_test_redis() -> fakeredis.FakeRedis:
    """Test Redis client dependency"""
    return test_redis_client

