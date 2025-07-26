"""
Database configuration and session management for driver service
"""
from sqlmodel import SQLModel, create_engine, Session
from config import settings
import redis
import logging

logger = logging.getLogger(__name__)

# Database engine with connection pooling
engine = create_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.debug
)

# Redis client
redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30
)


def create_db_and_tables():
    """Create database tables"""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


def get_session():
    """Get database session"""
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()


def get_redis():
    """Get Redis client"""
    try:
        # Test connection
        redis_client.ping()
        return redis_client
    except Exception as e:
        logger.error(f"Redis connection error: {str(e)}")
        raise


# Health check functions
def check_database_health() -> bool:
    """Check database connectivity"""
    try:
        with Session(engine) as session:
            session.exec("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False


def check_redis_health() -> bool:
    """Check Redis connectivity"""
    try:
        redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return False


def get_health_status() -> dict:
    """Get overall health status"""
    return {
        "database": check_database_health(),
        "redis": check_redis_health(),
        "status": "healthy" if check_database_health() and check_redis_health() else "unhealthy"
    }