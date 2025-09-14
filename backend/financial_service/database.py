"""
Database configuration and session management
"""
from sqlmodel import SQLModel, create_engine, Session
from config import settings
import redis
from typing import Generator


# PostgreSQL engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300
)

# Redis client
redis_client = redis.from_url(settings.redis_url, decode_responses=True)


"""
def create_db_and_tables():
    "Create database tables"
    SQLModel.metadata.create_all(engine)
"""


def get_session() -> Generator[Session, None, None]:
    """Database session dependency"""
    with Session(engine) as session:
        yield session


def get_redis() -> redis.Redis:
    """Redis client dependency"""
    return redis_client