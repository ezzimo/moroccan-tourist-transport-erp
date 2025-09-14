"""
Dependency injection providers for booking service
"""
from typing import Generator
from sqlmodel import Session, create_engine
from functools import lru_cache
import redis.asyncio as redis
from config import settings

# Database engine (singleton)
@lru_cache()
def get_engine():
    """Get database engine"""
    return create_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,
        pool_recycle=300
    )

def get_db() -> Generator[Session, None, None]:
    """Database session dependency"""
    engine = get_engine()
    with Session(engine) as session:
        yield session

# Redis client (singleton)
_redis_client = None

async def get_redis() -> redis.Redis:
    """Redis client dependency - matches auth_service pattern"""
    global _redis_client
    if _redis_client is None:
        # Use redis_url if available, otherwise build from components
        redis_url = getattr(settings, "redis_url", None)
        if not redis_url:
            # Fallback to component-based construction
            redis_host = getattr(settings, "redis_host", "localhost")
            redis_port = getattr(settings, "redis_port", 6379)
            redis_db = getattr(settings, "redis_db", 0)
            redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"
        
        _redis_client = redis.from_url(redis_url, decode_responses=True)
    
    return _redis_client