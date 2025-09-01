"""
Dependency injection providers for booking service
"""
from typing import AsyncGenerator
from sqlmodel import Session, create_engine
from sqlalchemy.pool import StaticPool
import redis.asyncio as redis
from fastapi import Depends
from config import settings

# Database engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300,
    poolclass=StaticPool if "sqlite" in settings.database_url else None,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Redis client (global instance)
_redis_client = None

async def get_session() -> AsyncGenerator[Session, None]:
    """Database session dependency"""
    with Session(engine) as session:
        yield session

async def get_redis() -> redis.Redis:
    """Redis client dependency - matches auth_service style"""
    global _redis_client
    if _redis_client is None:
        # Build Redis URL from settings
        redis_url = getattr(settings, "redis_url", None)
        if not redis_url:
            # Fallback construction if redis_url not set
            redis_host = getattr(settings, "redis_host", "localhost")
            redis_port = getattr(settings, "redis_port", 6379)
            redis_db = getattr(settings, "redis_db", 0)
            redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"
        
        _redis_client = redis.from_url(redis_url, decode_responses=True)
    
    return _redis_client

# Aliases for backward compatibility
get_db = get_session