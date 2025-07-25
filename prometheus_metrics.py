"""
Prometheus metrics integration for TradeWise AI
Exposes application metrics in Prometheus format for monitoring
"""

import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import Response
import threading

# Define Prometheus metrics
# Request metrics
request_count = Counter(
    'flask_request_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

request_duration = Histogram(
    'flask_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

request_exceptions = Counter(
    'flask_request_exceptions_total',
    'Total number of HTTP request exceptions',
    ['method', 'endpoint', 'exception']
)

# TradeWise AI specific metrics
stock_analysis_requests = Counter(
    'tradewise_stock_analysis_total',
    'Total number of stock analysis requests',
    ['symbol', 'user_tier']
)

cache_operations = Counter(
    'tradewise_cache_operations_total',
    'Total cache operations',
    ['operation', 'result']
)

cache_hit_rate = Gauge(
    'tradewise_cache_hit_rate',
    'Current cache hit rate'
)

task_queue_length = Gauge(
    'tradewise_task_queue_length',
    'Current task queue length'
)

task_operations = Counter(
    'tradewise_tasks_total',
    'Total task operations',
    ['operation', 'result']
)

active_users = Gauge(
    'tradewise_active_users',
    'Current number of active users'
)

ai_model_requests = Counter(
    'tradewise_ai_model_requests_total',
    'Total AI model requests',
    ['model_type', 'strategy']
)

ai_model_latency = Histogram(
    'tradewise_ai_model_latency_seconds',
    'AI model response latency',
    ['model_type']
)

database_operations = Counter(
    'tradewise_database_operations_total',
    'Total database operations',
    ['operation', 'table', 'result']
)

precomputation_service_running = Gauge(
    'tradewise_precomputation_service_running',
    'Whether precomputation service is running (1=running, 0=stopped)'
)

class PrometheusMetrics:
    """Prometheus metrics integration for Flask applications"""
    
    def __init__(self, app=None):
        self.app = app
        self._lock = threading.Lock()
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Prometheus metrics with Flask app"""
        # Add metrics endpoint
        @app.route('/metrics')
        def metrics_endpoint():
            return Response(
                generate_latest(),
                mimetype=CONTENT_TYPE_LATEST
            )
        
        # Track request metrics
        app.before_request(self._before_request)
        app.after_request(self._after_request)
    
    def _before_request(self):
        """Record request start time"""
        from flask import g
        g.start_time = time.time()
    
    def _after_request(self, response):
        """Record request metrics"""
        from flask import g, request
        
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Record request metrics
            request_count.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status_code=response.status_code
            ).inc()
            
            request_duration.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown'
            ).observe(duration)
        
        return response
    
    def record_exception(self, method, endpoint, exception_type):
        """Record request exception"""
        request_exceptions.labels(
            method=method,
            endpoint=endpoint,
            exception=exception_type
        ).inc()
    
    def record_stock_analysis(self, symbol, user_tier='free'):
        """Record stock analysis request"""
        stock_analysis_requests.labels(
            symbol=symbol,
            user_tier=user_tier
        ).inc()
    
    def record_cache_operation(self, operation, result):
        """Record cache operation (hit/miss)"""
        cache_operations.labels(
            operation=operation,
            result=result
        ).inc()
    
    def update_cache_hit_rate(self, hit_rate):
        """Update current cache hit rate"""
        cache_hit_rate.set(hit_rate)
    
    def update_task_queue_length(self, length):
        """Update current task queue length"""
        task_queue_length.set(length)
    
    def record_task_operation(self, operation, result):
        """Record task operation"""
        task_operations.labels(
            operation=operation,
            result=result
        ).inc()
    
    def update_active_users(self, count):
        """Update active user count"""
        active_users.set(count)
    
    def record_ai_model_request(self, model_type, strategy='default'):
        """Record AI model request"""
        ai_model_requests.labels(
            model_type=model_type,
            strategy=strategy
        ).inc()
    
    def record_ai_model_latency(self, model_type, duration):
        """Record AI model latency"""
        ai_model_latency.labels(
            model_type=model_type
        ).observe(duration)
    
    def record_database_operation(self, operation, table, result):
        """Record database operation"""
        database_operations.labels(
            operation=operation,
            table=table,
            result=result
        ).inc()
    
    def update_precomputation_status(self, running):
        """Update precomputation service status"""
        precomputation_service_running.set(1 if running else 0)

# Global metrics instance
prometheus_metrics = PrometheusMetrics()

# Convenience functions for easy use throughout the application
def record_stock_analysis(symbol, user_tier='free'):
    """Record a stock analysis request"""
    prometheus_metrics.record_stock_analysis(symbol, user_tier)

def record_cache_hit():
    """Record a cache hit"""
    prometheus_metrics.record_cache_operation('get', 'hit')

def record_cache_miss():
    """Record a cache miss"""
    prometheus_metrics.record_cache_operation('get', 'miss')

def update_cache_hit_rate(hit_rate):
    """Update cache hit rate"""
    prometheus_metrics.update_cache_hit_rate(hit_rate)

def update_task_queue_length(length):
    """Update task queue length"""
    prometheus_metrics.update_task_queue_length(length)

def record_task_completed():
    """Record a completed task"""
    prometheus_metrics.record_task_operation('process', 'success')

def record_task_failed():
    """Record a failed task"""
    prometheus_metrics.record_task_operation('process', 'failure')

def record_ai_request(model_type, strategy='default', duration=None):
    """Record AI model request and optionally latency"""
    prometheus_metrics.record_ai_model_request(model_type, strategy)
    if duration is not None:
        prometheus_metrics.record_ai_model_latency(model_type, duration)

def record_db_operation(operation, table, success=True):
    """Record database operation"""
    result = 'success' if success else 'failure'
    prometheus_metrics.record_database_operation(operation, table, result)

def update_precomputation_status(running):
    """Update precomputation service status"""
    prometheus_metrics.update_precomputation_status(running)