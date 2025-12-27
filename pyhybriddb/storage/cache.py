"""
Cache Manager - LRU Cache implementation for storage engine
"""

from typing import Dict, Any, Optional
from collections import OrderedDict

class CacheManager:
    """Least Recently Used (LRU) Cache"""

    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache: OrderedDict[str, Any] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key in self.cache:
            self.hits += 1
            self.cache.move_to_end(key)
            return self.cache[key]
        self.misses += 1
        return None

    def put(self, key: str, value: Any):
        """Put item into cache"""
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value

        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def invalidate(self, key: str):
        """Remove item from cache"""
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_ratio = (self.hits / total) if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'size': len(self.cache),
            'capacity': self.capacity,
            'hit_ratio': round(hit_ratio, 2)
        }
