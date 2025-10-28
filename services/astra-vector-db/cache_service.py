"""
Cache Service
Redis-based caching for frequent queries
"""
import os
import logging
import json
import hashlib
from typing import Optional, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"


class CacheService:
    """
    Redis-based cache for search results
    
    Features:
    - Query result caching
    - TTL management
    - Cache statistics
    """
    
    def __init__(self):
        self.enabled = ENABLE_CACHE
        self.ttl = CACHE_TTL
        self.redis_client = None
        
        # Stats
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0
        }
        
        if self.enabled:
            self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            import redis
            self.redis_client = redis.from_url(
                REDIS_URL,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis cache connected")
        
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {e}, cache disabled")
            self.enabled = False
    
    def _generate_key(self, query: str, filters: Optional[dict] = None) -> str:
        """Generate cache key from query and filters"""
        # Create unique key
        key_data = {
            "query": query,
            "filters": filters or {}
        }
        key_str = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"astra:search:{key_hash}"
    
    async def get(
        self,
        query: str,
        filters: Optional[dict] = None
    ) -> Optional[List[dict]]:
        """
        Get cached search results
        
        Returns:
            Cached results or None if not found
        """
        if not self.enabled:
            return None
        
        try:
            key = self._generate_key(query, filters)
            cached = self.redis_client.get(key)
            
            if cached:
                self.stats["hits"] += 1
                logger.info(f"✅ Cache HIT: {query[:50]}...")
                return json.loads(cached)
            else:
                self.stats["misses"] += 1
                logger.info(f"ℹ️ Cache MISS: {query[:50]}...")
                return None
        
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.stats["errors"] += 1
            return None
    
    async def set(
        self,
        query: str,
        results: List[dict],
        filters: Optional[dict] = None,
        ttl: Optional[int] = None
    ):
        """
        Cache search results
        
        Args:
            query: Search query
            results: Search results to cache
            filters: Optional filters used
            ttl: Time to live in seconds (default: CACHE_TTL)
        """
        if not self.enabled:
            return
        
        try:
            key = self._generate_key(query, filters)
            value = json.dumps(results)
            ttl = ttl or self.ttl
            
            self.redis_client.setex(key, ttl, value)
            self.stats["sets"] += 1
            logger.info(f"✅ Cached results for: {query[:50]}...")
        
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.stats["errors"] += 1
    
    async def invalidate(self, pattern: str = "astra:search:*"):
        """Invalidate cache entries matching pattern"""
        if not self.enabled:
            return
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"✅ Invalidated {len(keys)} cache entries")
        
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
            self.stats["errors"] += 1
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate_percentage": round(hit_rate, 2),
            "enabled": self.enabled
        }
    
    def health_check(self) -> dict:
        """Check cache health"""
        if not self.enabled:
            return {"status": "disabled"}
        
        try:
            self.redis_client.ping()
            return {
                "status": "healthy",
                "connected": True
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }


# Singleton
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get cache service singleton"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
