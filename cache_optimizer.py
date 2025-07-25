"""
Cache optimization strategies for TradeWise AI
Implements intelligent caching for market data, AI analysis, and search endpoints
"""

from functools import wraps
from flask import request, jsonify
import hashlib
import json
from app import cache
from performance_monitor import track_cache_hit, track_cache_miss
import logging

logger = logging.getLogger(__name__)

class CacheStrategy:
    """Intelligent caching strategies for different endpoint types"""
    
    # Cache timeouts for different data types
    CACHE_TIMEOUTS = {
        'market_data': 300,      # 5 minutes - market overview, movers
        'search_results': 60,    # 1 minute - search suggestions
        'ai_analysis': 60,       # 1 minute - AI insights (can change with market)
        'static_data': 3600,     # 1 hour - company info, sector data
        'user_preferences': 1800, # 30 minutes - user strategy, settings
        'stock_info': 180,       # 3 minutes - individual stock data
    }
    
    @staticmethod
    def smart_cache_key(prefix, **kwargs):
        """Generate intelligent cache keys based on parameters"""
        # Sort parameters for consistent keys
        sorted_params = sorted(kwargs.items())
        param_string = json.dumps(sorted_params, sort_keys=True)
        param_hash = hashlib.md5(param_string.encode()).hexdigest()[:8]
        return f"{prefix}:{param_hash}"
    
    @staticmethod
    def market_data_cache(timeout=None):
        """Cache decorator for market data endpoints"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_timeout = timeout or CacheStrategy.CACHE_TIMEOUTS['market_data']
                
                # Generate cache key
                cache_key = CacheStrategy.smart_cache_key(
                    f"market:{f.__name__}",
                    args=args,
                    kwargs=kwargs
                )
                
                # Try to get from cache
                cached_result = cache.get(cache_key)
                if cached_result:
                    track_cache_hit()
                    logger.debug(f"Cache HIT for {cache_key}")
                    return cached_result
                
                # Cache miss - execute function
                track_cache_miss()
                logger.debug(f"Cache MISS for {cache_key}")
                result = f(*args, **kwargs)
                
                # Cache the result if successful
                if isinstance(result, dict) and result.get('success', True):
                    cache.set(cache_key, result, timeout=cache_timeout)
                
                return result
            return decorated_function
        return decorator
    
    @staticmethod
    def ai_analysis_cache(timeout=None):
        """Cache decorator for AI analysis endpoints"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_timeout = timeout or CacheStrategy.CACHE_TIMEOUTS['ai_analysis']
                
                # Include user strategy in cache key for personalization
                user_strategy = request.args.get('strategy', 'default')
                cache_key = CacheStrategy.smart_cache_key(
                    f"ai:{f.__name__}",
                    args=args,
                    kwargs=kwargs,
                    strategy=user_strategy
                )
                
                cached_result = cache.get(cache_key)
                if cached_result:
                    track_cache_hit()
                    return cached_result
                
                track_cache_miss()
                result = f(*args, **kwargs)
                
                # Cache AI results
                if isinstance(result, dict) and result.get('success', True):
                    cache.set(cache_key, result, timeout=cache_timeout)
                
                return result
            return decorated_function
        return decorator
    
    @staticmethod
    def search_cache(timeout=None):
        """Cache decorator for search endpoints"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_timeout = timeout or CacheStrategy.CACHE_TIMEOUTS['search_results']
                
                # Include query parameters in cache key
                query = request.args.get('query', '').lower()
                cache_key = CacheStrategy.smart_cache_key(
                    f"search:{f.__name__}",
                    query=query,
                    args=args,
                    kwargs=kwargs
                )
                
                cached_result = cache.get(cache_key)
                if cached_result:
                    track_cache_hit()
                    return cached_result
                
                track_cache_miss()
                result = f(*args, **kwargs)
                
                # Cache search results
                if isinstance(result, dict) and result.get('success', True):
                    cache.set(cache_key, result, timeout=cache_timeout)
                
                return result
            return decorated_function
        return decorator
    
    @staticmethod
    def stock_data_cache(timeout=None):
        """Cache decorator for individual stock data"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_timeout = timeout or CacheStrategy.CACHE_TIMEOUTS['stock_info']
                
                # Extract symbol from args or request
                symbol = None
                if args:
                    symbol = args[0]
                elif 'symbol' in kwargs:
                    symbol = kwargs['symbol']
                else:
                    symbol = request.json.get('symbol') if request.json else request.args.get('symbol')
                
                cache_key = CacheStrategy.smart_cache_key(
                    f"stock:{f.__name__}",
                    symbol=symbol,
                    args=args[1:] if args else [],  # Exclude symbol from args
                    kwargs=kwargs
                )
                
                cached_result = cache.get(cache_key)
                if cached_result:
                    track_cache_hit()
                    return cached_result
                
                track_cache_miss()
                result = f(*args, **kwargs)
                
                # Cache stock data
                if isinstance(result, dict) and result.get('success', True):
                    cache.set(cache_key, result, timeout=cache_timeout)
                
                return result
            return decorated_function
        return decorator

# Cache management utilities
class CacheManager:
    """Utilities for cache management and optimization"""
    
    @staticmethod
    def clear_market_cache():
        """Clear all market data caches"""
        # Note: Flask-Caching 'simple' backend doesn't support pattern deletion
        # In production, consider Redis for advanced cache management
        cache.clear()
        logger.info("Market data cache cleared")
    
    @staticmethod
    def get_cache_stats():
        """Get cache statistics"""
        return {
            'cache_type': 'simple',
            'timeouts': CacheStrategy.CACHE_TIMEOUTS,
            'status': 'active'
        }
    
    @staticmethod
    def preload_popular_stocks():
        """Preload cache for popular stocks"""
        popular_stocks = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META']
        
        # This would typically call the stock analysis functions
        # to populate cache during low-traffic periods
        logger.info(f"Preloading cache for {len(popular_stocks)} popular stocks")
        return popular_stocks

# Create cache strategy instances
market_cache = CacheStrategy.market_data_cache
ai_cache = CacheStrategy.ai_analysis_cache
search_cache = CacheStrategy.search_cache
stock_cache = CacheStrategy.stock_data_cache