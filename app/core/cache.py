import redis
import json
from typing import Optional, Any
from app.config import settings

# Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class RedisCache:
    """Redis cache wrapper for efficient data caching"""
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set_cached_data(self, key: str, value: Any, ttl: int = settings.CACHE_TTL) -> bool:
        """Set value in cache with TTL"""
        try:
            serialized = json.dumps(value)
            redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def invalidate_cache(self, key_prefix: str) -> bool:
        """Clear all keys matching a pattern"""
        try:
            keys = redis_client.keys(f"{key_prefix}*")
            if keys:
                redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False


# Cache instance
redis_cache = RedisCache()