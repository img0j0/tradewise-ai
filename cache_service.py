"""
Cache service for optimizing API calls and improving performance
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class CacheService:
    """Simple in-memory cache for stock data and API responses"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_duration = 300  # 5 minutes in seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if it exists and is not expired"""
        if key in self._cache:
            cached_item = self._cache[key]
            if time.time() - cached_item['timestamp'] < self._cache_duration:
                return cached_item['data']
            else:
                # Remove expired item
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value with timestamp"""
        self._cache[key] = {
            'data': value,
            'timestamp': time.time()
        }
    
    def clear(self) -> None:
        """Clear all cached items"""
        self._cache.clear()
    
    def remove(self, key: str) -> None:
        """Remove specific key from cache"""
        if key in self._cache:
            del self._cache[key]
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        valid_items = 0
        expired_items = 0
        
        for key, value in self._cache.items():
            if current_time - value['timestamp'] < self._cache_duration:
                valid_items += 1
            else:
                expired_items += 1
        
        return {
            'total_items': len(self._cache),
            'valid_items': valid_items,
            'expired_items': expired_items,
            'cache_duration': self._cache_duration
        }

# Global cache instance
cache = CacheService()