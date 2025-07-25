"""
Performance monitoring middleware for TradeWise AI
Tracks response times, caching performance, and identifies optimization opportunities
"""

import time
import logging
import threading
from datetime import datetime
from functools import wraps
from flask import request, g
import json
import os

# Configure performance logging
performance_logger = logging.getLogger('performance')
performance_handler = logging.FileHandler('performance.log')
performance_formatter = logging.Formatter(
    '%(asctime)s - %(message)s'
)
performance_handler.setFormatter(performance_formatter)
performance_logger.addHandler(performance_handler)
performance_logger.setLevel(logging.INFO)

# Thread-safe performance metrics storage
performance_metrics = {
    'endpoint_stats': {},
    'slow_queries': [],
    'cache_stats': {'hits': 0, 'misses': 0},
    'lock': threading.Lock()
}

class PerformanceMonitor:
    """Lightweight performance monitoring for Flask applications"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize performance monitoring with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Add performance route for metrics
        @app.route('/api/performance/stats')
        def performance_stats():
            return self.get_performance_stats()
    
    def before_request(self):
        """Record request start time"""
        g.start_time = time.time()
        g.request_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(request)}"
    
    def after_request(self, response):
        """Record response time and log performance metrics"""
        if hasattr(g, 'start_time'):
            duration_ms = (time.time() - g.start_time) * 1000
            
            # Log performance data asynchronously
            threading.Thread(
                target=self._log_performance,
                args=(request.path, request.method, response.status_code, duration_ms)
            ).start()
            
            # Update metrics
            self._update_metrics(request.path, duration_ms)
            
            # Add performance headers
            response.headers['X-Response-Time'] = f"{duration_ms:.2f}ms"
            
        return response
    
    def _log_performance(self, path, method, status_code, duration_ms):
        """Asynchronously log performance data"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'path': path,
            'method': method,
            'status_code': status_code,
            'duration_ms': round(duration_ms, 2),
            'slow_request': duration_ms > 500
        }
        
        performance_logger.info(json.dumps(log_entry))
        
        # Track slow requests
        if duration_ms > 500:
            with performance_metrics['lock']:
                performance_metrics['slow_queries'].append(log_entry)
                # Keep only last 100 slow requests
                performance_metrics['slow_queries'] = performance_metrics['slow_queries'][-100:]
    
    def _update_metrics(self, path, duration_ms):
        """Update in-memory performance metrics"""
        with performance_metrics['lock']:
            if path not in performance_metrics['endpoint_stats']:
                performance_metrics['endpoint_stats'][path] = {
                    'count': 0,
                    'total_time': 0,
                    'avg_time': 0,
                    'max_time': 0,
                    'min_time': float('inf')
                }
            
            stats = performance_metrics['endpoint_stats'][path]
            stats['count'] += 1
            stats['total_time'] += duration_ms
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['max_time'] = max(stats['max_time'], duration_ms)
            stats['min_time'] = min(stats['min_time'], duration_ms)
    
    def get_performance_stats(self):
        """Get current performance statistics"""
        with performance_metrics['lock']:
            # Calculate slowest endpoints
            slowest_endpoints = sorted(
                performance_metrics['endpoint_stats'].items(),
                key=lambda x: x[1]['avg_time'],
                reverse=True
            )[:10]
            
            return {
                'success': True,
                'stats': {
                    'slowest_endpoints': [
                        {
                            'path': path,
                            'avg_time_ms': round(stats['avg_time'], 2),
                            'max_time_ms': round(stats['max_time'], 2),
                            'request_count': stats['count']
                        }
                        for path, stats in slowest_endpoints
                    ],
                    'slow_requests_count': len(performance_metrics['slow_queries']),
                    'recent_slow_requests': performance_metrics['slow_queries'][-5:],
                    'cache_hit_ratio': self._calculate_cache_ratio(),
                    'total_endpoints_tracked': len(performance_metrics['endpoint_stats'])
                }
            }
    
    def _calculate_cache_ratio(self):
        """Calculate cache hit ratio"""
        hits = performance_metrics['cache_stats']['hits']
        misses = performance_metrics['cache_stats']['misses']
        total = hits + misses
        return round((hits / total * 100), 2) if total > 0 else 0

def track_cache_hit():
    """Mark a cache hit"""
    with performance_metrics['lock']:
        performance_metrics['cache_stats']['hits'] += 1

def track_cache_miss():
    """Mark a cache miss"""
    with performance_metrics['lock']:
        performance_metrics['cache_stats']['misses'] += 1

def performance_optimized(cache_timeout=300):
    """Decorator to add caching and performance tracking to endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            # Execute function
            result = f(*args, **kwargs)
            
            # Track execution time
            execution_time = (time.time() - start_time) * 1000
            
            # Log if slow
            if execution_time > 100:  # Log operations > 100ms
                performance_logger.info(json.dumps({
                    'function': f.__name__,
                    'execution_time_ms': round(execution_time, 2),
                    'type': 'function_performance'
                }))
            
            return result
        return decorated_function
    return decorator

# Initialize performance monitor instance
monitor = PerformanceMonitor()