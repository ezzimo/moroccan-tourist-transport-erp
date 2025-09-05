"""
Locking utilities for preventing double-booking
"""
import redis
from typing import Optional
from datetime import datetime, timedelta
from ..config import settings
import uuid


class BookingLock:
    """Distributed locking for booking operations"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.lock_timeout = 300  # 5 minutes
    
    def acquire_lock(self, resource_key: str, lock_id: str = None) -> Optional[str]:
        """Acquire a distributed lock"""
        if not lock_id:
            lock_id = str(uuid.uuid4())
        
        lock_key = f"booking_lock:{resource_key}"
        
        # Try to acquire lock with expiration
        acquired = self.redis.set(
            lock_key, 
            lock_id, 
            nx=True,  # Only set if key doesn't exist
            ex=self.lock_timeout  # Expire after timeout
        )
        
        return lock_id if acquired else None
    
    def release_lock(self, resource_key: str, lock_id: str) -> bool:
        """Release a distributed lock"""
        lock_key = f"booking_lock:{resource_key}"
        
        # Lua script to atomically check and delete
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = self.redis.eval(lua_script, 1, lock_key, lock_id)
        return bool(result)
    
    def extend_lock(self, resource_key: str, lock_id: str, extend_seconds: int = 300) -> bool:
        """Extend lock expiration"""
        lock_key = f"booking_lock:{resource_key}"
        
        # Lua script to atomically check and extend
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("expire", KEYS[1], ARGV[2])
        else
            return 0
        end
        """
        
        result = self.redis.eval(lua_script, 1, lock_key, lock_id, extend_seconds)
        return bool(result)


def acquire_booking_lock(redis_client: redis.Redis, resource_type: str, resource_id: str, date: str) -> Optional[str]:
    """Acquire booking lock for specific resource and date"""
    resource_key = f"{resource_type}:{resource_id}:{date}"
    lock_manager = BookingLock(redis_client)
    return lock_manager.acquire_lock(resource_key)


def release_booking_lock(redis_client: redis.Redis, resource_type: str, resource_id: str, date: str, lock_id: str) -> bool:
    """Release booking lock"""
    resource_key = f"{resource_type}:{resource_id}:{date}"
    lock_manager = BookingLock(redis_client)
    return lock_manager.release_lock(resource_key, lock_id)