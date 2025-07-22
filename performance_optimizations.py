"""
Performance Optimizations for TradeWise AI
Comprehensive caching, database optimizations, and response improvements
"""

import time
import json
import hashlib
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify, g
from flask_caching import Cache
import yfinance as yf
import logging

# Configure cache
cache = Cache()

# Performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.request_times = []
    
    def start_timer(self, operation):
        g.start_time = time.time()
        g.operation = operation
    
    def end_timer(self):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            self.request_times.append(duration)
            operation = getattr(g, 'operation', 'unknown')
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(duration)
            return duration
        return 0
    
    def get_avg_response_time(self):
        if not self.request_times:
            return 0
        return sum(self.request_times) / len(self.request_times)
    
    def get_performance_stats(self):
        stats = {}
        for operation, times in self.metrics.items():
            stats[operation] = {
                'avg_time': sum(times) / len(times),
                'max_time': max(times),
                'min_time': min(times),
                'total_calls': len(times)
            }
        return stats

# Global performance monitor
perf_monitor = PerformanceMonitor()

def performance_timer(operation_name):
    """Decorator to time function execution"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            result = f(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            
            # Log slow operations
            if duration > 1.0:  # Log operations taking more than 1 second
                logging.warning(f"Slow operation {operation_name}: {duration:.2f}s")
            
            return result
        return decorated_function
    return decorator

# Advanced caching strategies
class SmartCache:
    def __init__(self, cache_instance):
        self.cache = cache_instance
    
    def cache_key(self, *args, **kwargs):
        """Generate consistent cache keys"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_stock_data(self, symbol, period="1d", use_cache=True):
        """Cached stock data retrieval with smart invalidation"""
        cache_key = f"stock_data_{symbol}_{period}"
        
        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                # Check if data is recent enough (within last 5 minutes for real-time)
                if cached_data.get('timestamp'):
                    cache_time = datetime.fromisoformat(cached_data['timestamp'])
                    if datetime.now() - cache_time < timedelta(minutes=5):
                        return cached_data['data']
        
        try:
            # Fetch fresh data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            info = ticker.info
            
            stock_data = {
                'symbol': symbol,
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'market_cap': info.get('marketCap', 0),
                'volume': info.get('volume', 0),
                'day_change': info.get('regularMarketChangePercent', 0),
                'history': hist.tail(20).to_dict('records') if not hist.empty else [],
                'company_name': info.get('longName', symbol)
            }
            
            # Cache with timestamp
            cached_entry = {
                'data': stock_data,
                'timestamp': datetime.now().isoformat()
            }
            self.cache.set(cache_key, cached_entry, timeout=300)  # Cache for 5 minutes
            
            return stock_data
            
        except Exception as e:
            logging.error(f"Error fetching stock data for {symbol}: {e}")
            return None
    
    def get_market_scan_data(self, symbols_list, use_cache=True):
        """Bulk fetch market data with intelligent caching"""
        cache_key = f"market_scan_{hashlib.md5(str(sorted(symbols_list)).encode()).hexdigest()}"
        
        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data and cached_data.get('timestamp'):
                cache_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cache_time < timedelta(minutes=3):
                    return cached_data['data']
        
        market_data = {}
        for symbol in symbols_list:
            stock_data = self.get_stock_data(symbol, period="5d", use_cache=True)
            if stock_data:
                market_data[symbol] = stock_data
        
        # Cache bulk result
        cached_entry = {
            'data': market_data,
            'timestamp': datetime.now().isoformat()
        }
        self.cache.set(cache_key, cached_entry, timeout=180)  # Cache for 3 minutes
        
        return market_data

# Database optimization helpers
class DatabaseOptimizer:
    @staticmethod
    def optimize_queries():
        """Database optimization strategies"""
        optimizations = {
            'connection_pooling': True,
            'query_caching': True,
            'index_optimization': True,
            'batch_operations': True
        }
        return optimizations
    
    @staticmethod
    def batch_insert(model_class, data_list, batch_size=100):
        """Batch insert for better performance"""
        from app import db
        try:
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i + batch_size]
                db.session.bulk_insert_mappings(model_class, batch)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"Batch insert error: {e}")
            return False

# Response optimization
class ResponseOptimizer:
    @staticmethod
    def compress_response(data):
        """Compress large responses"""
        if isinstance(data, dict) and len(str(data)) > 10000:
            # Remove unnecessary fields for large responses
            compressed = {}
            essential_fields = ['symbol', 'name', 'price', 'change', 'change_percent']
            
            if 'watchlist' in data:
                compressed['watchlist'] = []
                for item in data['watchlist']:
                    compressed_item = {k: v for k, v in item.items() if k in essential_fields}
                    compressed['watchlist'].append(compressed_item)
            
            return compressed
        return data
    
    @staticmethod
    def paginate_results(data, page=1, per_page=20):
        """Paginate large result sets"""
        if isinstance(data, list):
            start = (page - 1) * per_page
            end = start + per_page
            return {
                'data': data[start:end],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': len(data),
                    'has_next': end < len(data),
                    'has_prev': page > 1
                }
            }
        return data

# Memory optimization for large datasets
class MemoryOptimizer:
    @staticmethod
    def optimize_stock_history(hist_data):
        """Reduce memory usage of historical data"""
        if not hist_data or len(hist_data) == 0:
            return hist_data
        
        # Keep only essential columns and recent data
        essential_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        optimized = []
        
        for record in hist_data[-50:]:  # Keep only last 50 records
            optimized_record = {}
            for col in essential_cols:
                if col in record:
                    # Round to 2 decimal places to save memory
                    if col != 'Volume':
                        optimized_record[col] = round(float(record[col]), 2)
                    else:
                        optimized_record[col] = int(record[col])
            optimized.append(optimized_record)
        
        return optimized

# API rate limiting
class RateLimiter:
    def __init__(self):
        self.requests = {}
        self.limits = {
            'stock_data': {'calls': 100, 'period': 3600},  # 100 calls per hour
            'market_scan': {'calls': 20, 'period': 3600},   # 20 calls per hour
            'alerts': {'calls': 200, 'period': 3600}        # 200 calls per hour
        }
    
    def is_allowed(self, operation, client_id=None):
        """Check if operation is within rate limits"""
        if operation not in self.limits:
            return True
        
        key = f"{operation}_{client_id or 'default'}"
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the time window
        self.requests[key] = [req_time for req_time in self.requests[key] 
                             if now - req_time < self.limits[operation]['period']]
        
        # Check if within limits
        if len(self.requests[key]) < self.limits[operation]['calls']:
            self.requests[key].append(now)
            return True
        
        return False

# Initialize optimizers
smart_cache = None  # Will be initialized with Flask app
db_optimizer = DatabaseOptimizer()
response_optimizer = ResponseOptimizer()
memory_optimizer = MemoryOptimizer()
rate_limiter = RateLimiter()

def init_performance_optimizations(app):
    """Initialize performance optimizations with Flask app"""
    global smart_cache
    
    # Configure caching
    cache.init_app(app, config={
        'CACHE_TYPE': 'simple',  # Use Redis in production
        'CACHE_DEFAULT_TIMEOUT': 300
    })
    
    smart_cache = SmartCache(cache)
    
    # Add performance middleware
    @app.before_request
    def before_request():
        perf_monitor.start_timer(request.endpoint or 'unknown')
    
    @app.after_request
    def after_request(response):
        duration = perf_monitor.end_timer()
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        return response
    
    # Performance monitoring endpoint
    @app.route('/api/performance/stats')
    def performance_stats():
        return jsonify({
            'avg_response_time': perf_monitor.get_avg_response_time(),
            'performance_breakdown': perf_monitor.get_performance_stats(),
            'cache_stats': {
                'hit_rate': 'N/A',  # Would implement with Redis
                'memory_usage': 'N/A'
            }
        })
    
    return app