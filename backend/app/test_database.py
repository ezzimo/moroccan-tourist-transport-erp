"""
Test database configuration and session management
"""
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
import sqlite3
import fakeredis
from typing import Generator

# Always use SQLite for tests
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Fake Redis client for testing
test_redis_client = fakeredis.FakeRedis(decode_responses=True)


def _import_models() -> None:
    """
    Import all model modules so their tables get registered
    on SQLModel.metadata before create_all().
    """
    # Import the package that pulls all models into metadata
    # (models/__init__.py already exports User, Role, Permission, ActivityLog, etc.)
    # import models  # noqa: F401
    # If you prefer being explicit:
    from models.user import User, UserRole  # noqa: F401
    from models.role import Role, RolePermission  # noqa: F401
    from models.permission import Permission  # noqa: F401
    from models.activity_log import ActivityLog  # noqa: F401


def create_test_db_and_tables():
    _import_models()
    # Start clean every time
    SQLModel.metadata.drop_all(bind=test_engine)
    SQLModel.metadata.create_all(bind=test_engine)


def get_test_session() -> Generator[Session, None, None]:
    """Test database session dependency"""
    with Session(test_engine) as session:
        yield session


def get_test_redis() -> fakeredis.FakeRedis:
    """Test Redis client dependency"""
    return test_redis_client


@event.listens_for(test_engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
