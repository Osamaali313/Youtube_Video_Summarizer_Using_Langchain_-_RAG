"""
Redis caching layer for performance optimization
"""
import json
import hashlib
from typing import Optional, Any
from functools import wraps
import redis.asyncio as redis
from loguru import logger

from app.config import settings


class CacheManager:
    """Redis cache manager"""

    def __init__(self):
        """Initialize cache manager"""
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = settings.ENABLE_CACHE

    async def connect(self):
        """Connect to Redis"""
        if not self.enabled:
            logger.info("Caching disabled")
            return

        try:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
            self.enabled = False

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Create hashable string from args and kwargs
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))

        key_string = ":".join(key_parts)

        # Hash for consistent length
        key_hash = hashlib.md5(key_string.encode()).hexdigest()

        return f"{prefix}:{key_hash}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled or not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            else:
                logger.debug(f"Cache MISS: {key}")
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            ttl = ttl or settings.CACHE_TTL
            serialized = json.dumps(value)
            await self.redis_client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            await self.redis_client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.enabled or not self.redis_client:
            return 0

        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"Cache DELETE PATTERN: {pattern} ({deleted} keys)")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return 0

    async def clear(self) -> bool:
        """Clear all cache"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            await self.redis_client.flushdb()
            logger.info("Cache CLEARED")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

    def cache_key(self, prefix: str, ttl: Optional[int] = None):
        """
        Decorator for caching function results

        Usage:
            @cache_manager.cache_key("summary", ttl=3600)
            async def get_summary(video_id: str):
                ...
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                key = self._generate_key(prefix, *args, **kwargs)

                # Try to get from cache
                cached_value = await self.get(key)
                if cached_value is not None:
                    return cached_value

                # Call function
                result = await func(*args, **kwargs)

                # Cache result
                if result is not None:
                    await self.set(key, result, ttl)

                return result

            return wrapper
        return decorator


# Global cache manager instance
cache_manager = CacheManager()


# Specialized cache functions for common operations
class VideoCache:
    """Video-specific caching functions"""

    @staticmethod
    async def get_summary(video_id: str, mode: str) -> Optional[dict]:
        """Get cached summary"""
        key = f"summary:{video_id}:{mode}"
        return await cache_manager.get(key)

    @staticmethod
    async def set_summary(video_id: str, mode: str, summary: dict, ttl: int = 3600):
        """Cache summary"""
        key = f"summary:{video_id}:{mode}"
        await cache_manager.set(key, summary, ttl)

    @staticmethod
    async def get_transcript(video_id: str) -> Optional[dict]:
        """Get cached transcript"""
        key = f"transcript:{video_id}"
        return await cache_manager.get(key)

    @staticmethod
    async def set_transcript(video_id: str, transcript: dict, ttl: int = 7200):
        """Cache transcript (longer TTL)"""
        key = f"transcript:{video_id}"
        await cache_manager.set(key, transcript, ttl)

    @staticmethod
    async def invalidate_video(video_id: str):
        """Invalidate all cache for a video"""
        await cache_manager.delete_pattern(f"*:{video_id}:*")


class RateLimitCache:
    """Rate limiting using Redis"""

    @staticmethod
    async def check_rate_limit(
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check if request is within rate limit

        Args:
            identifier: Unique identifier (IP, API key, etc.)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            (allowed: bool, remaining: int)
        """
        if not cache_manager.enabled or not cache_manager.redis_client:
            return True, max_requests

        try:
            key = f"ratelimit:{identifier}"

            # Increment counter
            current = await cache_manager.redis_client.incr(key)

            # Set expiry on first request
            if current == 1:
                await cache_manager.redis_client.expire(key, window_seconds)

            # Check limit
            allowed = current <= max_requests
            remaining = max(0, max_requests - current)

            if not allowed:
                logger.warning(f"Rate limit exceeded for {identifier}")

            return allowed, remaining

        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True, max_requests  # Allow on error


# Video cache instance
video_cache = VideoCache()


# Rate limit cache instance
rate_limit_cache = RateLimitCache()
