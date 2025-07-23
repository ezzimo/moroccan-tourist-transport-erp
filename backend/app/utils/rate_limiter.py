"""
Rate limiting utilities for API endpoints
"""
from fastapi import HTTPException, Request, status
from datetime import datetime, timedelta
import redis
from typing import Optional


class RateLimiter:
    """Rate limiter using Redis for tracking attempts"""
    
    def __init__(self, redis_client: redis.Redis, max_attempts: int, window_minutes: int):
        self.redis = redis_client
        self.max_attempts = max_attempts
        self.window_seconds = window_minutes * 60
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed based on rate limit"""
        key = f"rate_limit:{identifier}"
        current_attempts = self.redis.get(key)
        
        if current_attempts is None:
            # First attempt
            self.redis.setex(key, self.window_seconds, 1)
            return True
        
        if int(current_attempts) >= self.max_attempts:
            return False
        
        # Increment counter
        self.redis.incr(key)
        return True
    
    def get_attempts(self, identifier: str) -> int:
        """Get current number of attempts"""
        attempts = self.redis.get(f"rate_limit:{identifier}")
        return int(attempts) if attempts else 0
    
    def reset(self, identifier: str):
        """Reset rate limit counter"""
        self.redis.delete(f"rate_limit:{identifier}")


def check_rate_limit(
    request: Request,
    redis_client: redis.Redis,
    max_attempts: int = 5,
    window_minutes: int = 1,
    identifier_func: Optional[callable] = None
) -> None:
    """Check rate limit for request"""
    if identifier_func:
        identifier = identifier_func(request)
    else:
        identifier = request.client.host
    
    rate_limiter = RateLimiter(redis_client, max_attempts, window_minutes)
    
    if not rate_limiter.is_allowed(identifier):
        attempts = rate_limiter.get_attempts(identifier)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. {attempts}/{max_attempts} attempts. Try again later."
        )