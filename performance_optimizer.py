"""
Performance Optimization Module
Advanced caching, WebSocket pooling, and system optimizations
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import asyncio
import threading
from collections import defaultdict, deque
import functools
import weakref
import hashlib
import pickle
import redis
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheManager:
    """Intelligent caching system with TTL and size limits"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = {}
        self.access_times = deque()
        self.lock = threading.RLock()
        
        # Try to use Redis if available
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
            self.redis_client.ping()
            self.use_redis = True
            logger.info("Redis cache enabled")
        except:
            self.use_redis = False
            logger.info("Using in-memory cache")
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            if self.use_redis:
                return self._redis_get(key)
            else:
                return self._memory_get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value"""
        try:
            if self.use_redis:
                return self._redis_set(key, value, ttl)
            else:
                return self._memory_set(key, value, ttl)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached value"""
        try:
            if self.use_redis:
                return self._redis_delete(key)
            else:
                return self._memory_delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cached values"""
        try:
            if self.use_redis:
                return self._redis_clear()
            else:
                return self._memory_clear()
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def _redis_get(self, key: str) -> Optional[Any]:
        """Redis get implementation"""
        data = self.redis_client.get(key)
        if data:
            return pickle.loads(data)
        return None
    
    def _redis_set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Redis set implementation"""
        ttl = ttl or self.default_ttl
        data = pickle.dumps(value)
        return self.redis_client.setex(key, ttl, data)
    
    def _redis_delete(self, key: str) -> bool:
        """Redis delete implementation"""
        return self.redis_client.delete(key) > 0
    
    def _redis_clear(self) -> bool:
        """Redis clear implementation"""
        return self.redis_client.flushdb()
    
    def _memory_get(self, key: str) -> Optional[Any]:
        """In-memory get implementation"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if expired
                if entry['expires'] < time.time():
                    del self.cache[key]
                    return None
                
                # Update access time
                self.access_times.append((key, time.time()))
                return entry['value']
            
            return None
    
    def _memory_set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """In-memory set implementation"""
        with self.lock:
            ttl = ttl or self.default_ttl
            
            # Evict if at capacity
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()
            
            self.cache[key] = {
                'value': value,
                'expires': time.time() + ttl,
                'created': time.time()
            }
            
            self.access_times.append((key, time.time()))
            return True
    
    def _memory_delete(self, key: str) -> bool:
        """In-memory delete implementation"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def _memory_clear(self) -> bool:
        """In-memory clear implementation"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            return True
    
    def _evict_lru(self):
        """Evict least recently used items"""
        # Remove oldest entries
        while len(self.access_times) > self.max_size:
            old_key, _ = self.access_times.popleft()
            if old_key in self.cache:
                del self.cache[old_key]
                break

class ConnectionPool:
    """WebSocket connection pool manager"""
    
    def __init__(self, max_connections: int = 100):
        self.max_connections = max_connections
        self.active_connections = {}
        self.connection_stats = defaultdict(lambda: {'created': 0, 'messages': 0})
        self.lock = threading.RLock()
        
        logger.info(f"Connection pool initialized with max_connections={max_connections}")
    
    def add_connection(self, connection_id: str, connection: Any) -> bool:
        """Add connection to pool"""
        with self.lock:
            if len(self.active_connections) >= self.max_connections:
                logger.warning("Connection pool at capacity")
                return False
            
            self.active_connections[connection_id] = {
                'connection': connection,
                'created_at': time.time(),
                'last_activity': time.time()
            }
            
            self.connection_stats[connection_id]['created'] += 1
            logger.info(f"Connection {connection_id} added to pool")
            return True
    
    def remove_connection(self, connection_id: str) -> bool:
        """Remove connection from pool"""
        with self.lock:
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
                logger.info(f"Connection {connection_id} removed from pool")
                return True
            return False
    
    def get_connection(self, connection_id: str) -> Optional[Any]:
        """Get connection from pool"""
        with self.lock:
            if connection_id in self.active_connections:
                entry = self.active_connections[connection_id]
                entry['last_activity'] = time.time()
                return entry['connection']
            return None
    
    def broadcast_message(self, message: Dict[str, Any], exclude: List[str] = None) -> int:
        """Broadcast message to all connections"""
        exclude = exclude or []
        sent_count = 0
        
        with self.lock:
            for connection_id, entry in self.active_connections.items():
                if connection_id not in exclude:
                    try:
                        connection = entry['connection']
                        # Assuming connection has an emit method
                        if hasattr(connection, 'emit'):
                            connection.emit('message', message)
                            self.connection_stats[connection_id]['messages'] += 1
                            sent_count += 1
                    except Exception as e:
                        logger.error(f"Error broadcasting to {connection_id}: {e}")
        
        return sent_count
    
    def cleanup_stale_connections(self, max_age: int = 3600):
        """Clean up stale connections"""
        current_time = time.time()
        stale_connections = []
        
        with self.lock:
            for connection_id, entry in self.active_connections.items():
                if current_time - entry['last_activity'] > max_age:
                    stale_connections.append(connection_id)
            
            for connection_id in stale_connections:
                self.remove_connection(connection_id)
        
        logger.info(f"Cleaned up {len(stale_connections)} stale connections")
        return len(stale_connections)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self.lock:
            return {
                'active_connections': len(self.active_connections),
                'max_connections': self.max_connections,
                'connection_stats': dict(self.connection_stats),
                'timestamp': time.time()
            }

class QueryOptimizer:
    """Database query optimization with caching and batching"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.query_batch = defaultdict(list)
        self.batch_timers = {}
        self.query_stats = defaultdict(lambda: {'count': 0, 'avg_time': 0})
        
        logger.info("Query Optimizer initialized")
    
    def cached_query(self, query_key: str, query_func: Callable, 
                    ttl: Optional[int] = None, *args, **kwargs) -> Any:
        """Execute query with caching"""
        # Check cache first
        cached_result = self.cache_manager.get(query_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for query: {query_key}")
            return cached_result
        
        # Execute query
        start_time = time.time()
        try:
            result = query_func(*args, **kwargs)
            
            # Cache result
            self.cache_manager.set(query_key, result, ttl)
            
            # Update stats
            execution_time = time.time() - start_time
            self._update_query_stats(query_key, execution_time)
            
            logger.debug(f"Query executed and cached: {query_key} ({execution_time:.3f}s)")
            return result
            
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise
    
    def batch_query(self, batch_key: str, query_func: Callable, 
                   delay: float = 0.1, *args, **kwargs):
        """Batch queries for efficient execution"""
        self.query_batch[batch_key].append((query_func, args, kwargs))
        
        # Set timer for batch execution
        if batch_key not in self.batch_timers:
            timer = threading.Timer(delay, self._execute_batch, [batch_key])
            self.batch_timers[batch_key] = timer
            timer.start()
    
    def _execute_batch(self, batch_key: str):
        """Execute batched queries"""
        queries = self.query_batch[batch_key]
        self.query_batch[batch_key] = []
        
        if batch_key in self.batch_timers:
            del self.batch_timers[batch_key]
        
        start_time = time.time()
        results = []
        
        for query_func, args, kwargs in queries:
            try:
                result = query_func(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch query error: {e}")
                results.append(None)
        
        execution_time = time.time() - start_time
        logger.info(f"Batch executed: {batch_key} ({len(queries)} queries, {execution_time:.3f}s)")
        
        return results
    
    def _update_query_stats(self, query_key: str, execution_time: float):
        """Update query statistics"""
        stats = self.query_stats[query_key]
        stats['count'] += 1
        stats['avg_time'] = (stats['avg_time'] * (stats['count'] - 1) + execution_time) / stats['count']
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        return dict(self.query_stats)

class PerformanceMonitor:
    """System performance monitoring and optimization"""
    
    def __init__(self):
        self.metrics = {
            'requests_per_second': deque(maxlen=1000),
            'response_times': deque(maxlen=1000),
            'memory_usage': deque(maxlen=1000),
            'cache_hit_rate': deque(maxlen=1000),
            'active_connections': deque(maxlen=1000),
            'error_rate': deque(maxlen=1000)
        }
        
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        
        logger.info("Performance Monitor initialized")
    
    def record_request(self, response_time: float, error: bool = False):
        """Record request metrics"""
        current_time = time.time()
        
        self.request_count += 1
        if error:
            self.error_count += 1
        
        # Record metrics
        self.metrics['response_times'].append(response_time)
        
        # Calculate RPS over last 60 seconds
        minute_ago = current_time - 60
        recent_requests = sum(1 for t in self.metrics['requests_per_second'] 
                            if t > minute_ago)
        
        self.metrics['requests_per_second'].append(current_time)
        
        # Calculate error rate
        if self.request_count > 0:
            error_rate = self.error_count / self.request_count
            self.metrics['error_rate'].append(error_rate)
    
    def record_memory_usage(self, memory_mb: float):
        """Record memory usage"""
        self.metrics['memory_usage'].append(memory_mb)
    
    def record_cache_hit_rate(self, hit_rate: float):
        """Record cache hit rate"""
        self.metrics['cache_hit_rate'].append(hit_rate)
    
    def record_active_connections(self, count: int):
        """Record active connections"""
        self.metrics['active_connections'].append(count)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # Calculate recent averages
        recent_response_times = list(self.metrics['response_times'])[-100:]
        avg_response_time = sum(recent_response_times) / len(recent_response_times) if recent_response_times else 0
        
        recent_memory = list(self.metrics['memory_usage'])[-10:]
        avg_memory = sum(recent_memory) / len(recent_memory) if recent_memory else 0
        
        recent_cache_hits = list(self.metrics['cache_hit_rate'])[-10:]
        avg_cache_hit_rate = sum(recent_cache_hits) / len(recent_cache_hits) if recent_cache_hits else 0
        
        recent_connections = list(self.metrics['active_connections'])[-10:]
        avg_connections = sum(recent_connections) / len(recent_connections) if recent_connections else 0
        
        # Calculate RPS
        minute_ago = current_time - 60
        recent_requests = sum(1 for t in self.metrics['requests_per_second'] 
                            if t > minute_ago)
        
        return {
            'uptime': uptime,
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'requests_per_second': recent_requests,
            'avg_response_time': avg_response_time,
            'avg_memory_usage': avg_memory,
            'avg_cache_hit_rate': avg_cache_hit_rate,
            'avg_active_connections': avg_connections,
            'error_rate': self.error_count / self.request_count if self.request_count > 0 else 0,
            'timestamp': current_time
        }
    
    def get_performance_recommendations(self) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        metrics = self.get_current_metrics()
        
        # Response time recommendations
        if metrics['avg_response_time'] > 1.0:
            recommendations.append("High response times detected - consider query optimization")
        
        # Memory usage recommendations
        if metrics['avg_memory_usage'] > 1000:  # 1GB
            recommendations.append("High memory usage - consider cache cleanup")
        
        # Cache hit rate recommendations
        if metrics['avg_cache_hit_rate'] < 0.7:
            recommendations.append("Low cache hit rate - review caching strategy")
        
        # Error rate recommendations
        if metrics['error_rate'] > 0.05:  # 5%
            recommendations.append("High error rate - investigate error patterns")
        
        # Connection recommendations
        if metrics['avg_active_connections'] > 80:
            recommendations.append("High connection count - consider connection pooling")
        
        return recommendations

class PerformanceOptimizer:
    """Main performance optimization coordinator"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.connection_pool = ConnectionPool()
        self.query_optimizer = QueryOptimizer(self.cache_manager)
        self.performance_monitor = PerformanceMonitor()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Performance Optimizer initialized")
    
    def _start_background_tasks(self):
        """Start background optimization tasks"""
        # Cache cleanup task
        def cache_cleanup():
            while True:
                time.sleep(300)  # Run every 5 minutes
                try:
                    # Cleanup would happen automatically with TTL
                    # This is a placeholder for custom cleanup logic
                    pass
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")
        
        # Connection cleanup task
        def connection_cleanup():
            while True:
                time.sleep(600)  # Run every 10 minutes
                try:
                    self.connection_pool.cleanup_stale_connections()
                except Exception as e:
                    logger.error(f"Connection cleanup error: {e}")
        
        # Start background threads
        cache_thread = threading.Thread(target=cache_cleanup, daemon=True)
        connection_thread = threading.Thread(target=connection_cleanup, daemon=True)
        
        cache_thread.start()
        connection_thread.start()
        
        logger.info("Background optimization tasks started")
    
    def optimize_function(self, cache_key: str = None, ttl: int = 300):
        """Decorator for function optimization"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key if not provided
                if cache_key is None:
                    key_data = f"{func.__name__}:{args}:{kwargs}"
                    key = hashlib.md5(key_data.encode()).hexdigest()
                else:
                    key = cache_key
                
                # Use cached query optimizer
                return self.query_optimizer.cached_query(
                    key, func, ttl, *args, **kwargs
                )
            
            return wrapper
        return decorator
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report"""
        return {
            'cache_stats': {
                'type': 'redis' if self.cache_manager.use_redis else 'memory',
                'size': len(self.cache_manager.cache) if not self.cache_manager.use_redis else 'N/A'
            },
            'connection_stats': self.connection_pool.get_stats(),
            'query_stats': self.query_optimizer.get_query_stats(),
            'performance_metrics': self.performance_monitor.get_current_metrics(),
            'recommendations': self.performance_monitor.get_performance_recommendations(),
            'timestamp': datetime.now().isoformat()
        }

# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()

def get_performance_optimizer():
    """Get the global performance optimizer instance"""
    return performance_optimizer

# Convenience decorators
def cached(ttl: int = 300):
    """Caching decorator"""
    return performance_optimizer.optimize_function(ttl=ttl)

def monitored(func):
    """Performance monitoring decorator"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        error = False
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error = True
            raise
        finally:
            response_time = time.time() - start_time
            performance_optimizer.performance_monitor.record_request(response_time, error)
    
    return wrapper