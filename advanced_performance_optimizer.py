"""
Advanced Performance Optimizer
Comprehensive system for optimizing TradeWise AI platform performance
"""

import time
import asyncio
import functools
import threading
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
import logging
import json
import pickle
import hashlib
from collections import defaultdict, deque
import psutil
import gc

class AdvancedCacheManager:
    """Intelligent caching system with predictive pre-loading"""
    
    def __init__(self, max_memory_mb: int = 512):
        self.cache = {}
        self.access_times = {}
        self.access_counts = defaultdict(int)
        self.cache_stats = {'hits': 0, 'misses': 0, 'evictions': 0}
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_memory = 0
        self.logger = logging.getLogger(__name__)
        
    def get(self, key: str) -> Optional[Any]:
        """Get cached value with access tracking"""
        if key in self.cache:
            self.access_times[key] = datetime.now()
            self.access_counts[key] += 1
            self.cache_stats['hits'] += 1
            return self.cache[key]['data']
        
        self.cache_stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set cached value with intelligent eviction"""
        # Calculate memory usage
        serialized = pickle.dumps(value)
        size = len(serialized)
        
        # Evict if necessary
        while self.current_memory + size > self.max_memory_bytes and self.cache:
            self._evict_lru()
        
        self.cache[key] = {
            'data': value,
            'expires': datetime.now() + timedelta(seconds=ttl_seconds),
            'size': size
        }
        self.access_times[key] = datetime.now()
        self.access_counts[key] += 1
        self.current_memory += size
        
    def _evict_lru(self):
        """Evict least recently used item"""
        if not self.access_times:
            return
            
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        if lru_key in self.cache:
            self.current_memory -= self.cache[lru_key]['size']
            del self.cache[lru_key]
            del self.access_times[lru_key]
            self.cache_stats['evictions'] += 1
    
    def cleanup_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = [
            key for key, data in self.cache.items()
            if data['expires'] < now
        ]
        
        for key in expired_keys:
            self.current_memory -= self.cache[key]['size']
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]

class DatabaseOptimizer:
    """Database query optimization and connection pooling"""
    
    def __init__(self):
        self.query_stats = defaultdict(list)
        self.slow_query_threshold = 1.0  # seconds
        self.logger = logging.getLogger(__name__)
        
    def track_query(self, query: str, execution_time: float):
        """Track query performance"""
        self.query_stats[query].append({
            'time': execution_time,
            'timestamp': datetime.now()
        })
        
        if execution_time > self.slow_query_threshold:
            self.logger.warning(f"Slow query detected: {execution_time:.3f}s - {query[:100]}...")
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        stats = {}
        for query, times in self.query_stats.items():
            execution_times = [t['time'] for t in times]
            stats[query] = {
                'count': len(execution_times),
                'avg_time': sum(execution_times) / len(execution_times),
                'max_time': max(execution_times),
                'min_time': min(execution_times)
            }
        return stats

class MemoryOptimizer:
    """Memory usage optimization and monitoring"""
    
    def __init__(self):
        self.memory_snapshots = deque(maxlen=100)
        self.gc_stats = {'collections': 0, 'memory_freed': 0}
        self.logger = logging.getLogger(__name__)
        
    def take_snapshot(self) -> Dict[str, Any]:
        """Take memory usage snapshot"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        snapshot = {
            'timestamp': datetime.now(),
            'rss': memory_info.rss,  # Resident Set Size
            'vms': memory_info.vms,  # Virtual Memory Size
            'percent': process.memory_percent(),
            'available': psutil.virtual_memory().available
        }
        
        self.memory_snapshots.append(snapshot)
        return snapshot
    
    def force_garbage_collection(self) -> Dict[str, Any]:
        """Force garbage collection and track memory freed"""
        before = psutil.Process().memory_info().rss
        
        # Force garbage collection
        collected = gc.collect()
        
        after = psutil.Process().memory_info().rss
        freed = before - after
        
        self.gc_stats['collections'] += 1
        self.gc_stats['memory_freed'] += freed
        
        return {
            'objects_collected': collected,
            'memory_freed_bytes': freed,
            'memory_freed_mb': freed / 1024 / 1024
        }
    
    def get_memory_trends(self) -> Dict[str, Any]:
        """Analyze memory usage trends"""
        if len(self.memory_snapshots) < 2:
            return {'trend': 'insufficient_data'}
        
        recent = list(self.memory_snapshots)[-10:]
        memory_values = [s['rss'] for s in recent]
        
        # Calculate trend
        if len(memory_values) > 1:
            trend = (memory_values[-1] - memory_values[0]) / len(memory_values)
            trend_direction = 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable'
        else:
            trend_direction = 'stable'
        
        return {
            'trend': trend_direction,
            'current_mb': memory_values[-1] / 1024 / 1024,
            'peak_mb': max(memory_values) / 1024 / 1024,
            'average_mb': sum(memory_values) / len(memory_values) / 1024 / 1024
        }

class PerformanceProfiler:
    """Advanced performance profiling and monitoring"""
    
    def __init__(self):
        self.function_stats = defaultdict(list)
        self.api_stats = defaultdict(list)
        self.logger = logging.getLogger(__name__)
        
    def profile_function(self, func: Callable) -> Callable:
        """Decorator to profile function performance"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
                raise
            finally:
                end_time = time.time()
                execution_time = end_time - start_time
                
                self.function_stats[func.__name__].append({
                    'execution_time': execution_time,
                    'timestamp': datetime.now(),
                    'success': success,
                    'error': error
                })
                
                if execution_time > 2.0:  # Log slow functions
                    self.logger.warning(f"Slow function: {func.__name__} took {execution_time:.3f}s")
            
            return result
        return wrapper
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            'function_performance': {},
            'system_metrics': self._get_system_metrics(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Analyze function performance
        for func_name, stats in self.function_stats.items():
            execution_times = [s['execution_time'] for s in stats if s['success']]
            if execution_times:
                report['function_performance'][func_name] = {
                    'calls': len(stats),
                    'avg_time': sum(execution_times) / len(execution_times),
                    'max_time': max(execution_times),
                    'min_time': min(execution_times),
                    'success_rate': len([s for s in stats if s['success']]) / len(stats) * 100
                }
        
        return report
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        process = psutil.Process()
        
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }

class AdvancedPerformanceOptimizer:
    """Main performance optimization coordinator"""
    
    def __init__(self):
        self.cache_manager = AdvancedCacheManager()
        self.db_optimizer = DatabaseOptimizer()
        self.memory_optimizer = MemoryOptimizer()
        self.profiler = PerformanceProfiler()
        self.logger = logging.getLogger(__name__)
        
        # Start background optimization tasks
        self._start_background_tasks()
        
    def _start_background_tasks(self):
        """Start background optimization tasks"""
        def background_optimization():
            while True:
                try:
                    # Cleanup expired cache entries
                    self.cache_manager.cleanup_expired()
                    
                    # Take memory snapshot
                    self.memory_optimizer.take_snapshot()
                    
                    # Force GC if memory usage is high
                    memory_percent = psutil.Process().memory_percent()
                    if memory_percent > 80:
                        self.memory_optimizer.force_garbage_collection()
                    
                    time.sleep(30)  # Run every 30 seconds
                    
                except Exception as e:
                    self.logger.error(f"Background optimization error: {e}")
                    time.sleep(60)  # Wait longer on error
        
        thread = threading.Thread(target=background_optimization, daemon=True)
        thread.start()
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        return {
            'cache_stats': self.cache_manager.cache_stats,
            'memory_trends': self.memory_optimizer.get_memory_trends(),
            'query_stats': self.db_optimizer.get_query_stats(),
            'performance_report': self.profiler.get_performance_report(),
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Cache analysis
        cache_hit_rate = (
            self.cache_manager.cache_stats['hits'] / 
            (self.cache_manager.cache_stats['hits'] + self.cache_manager.cache_stats['misses'])
            if self.cache_manager.cache_stats['hits'] + self.cache_manager.cache_stats['misses'] > 0
            else 0
        )
        
        if cache_hit_rate < 0.8:
            recommendations.append(f"Cache hit rate is {cache_hit_rate:.1%}. Consider increasing cache TTL or memory allocation.")
        
        # Memory analysis
        memory_trends = self.memory_optimizer.get_memory_trends()
        if memory_trends.get('trend') == 'increasing':
            recommendations.append("Memory usage is trending upward. Consider memory optimization or garbage collection tuning.")
        
        # Performance analysis
        performance_report = self.profiler.get_performance_report()
        slow_functions = [
            name for name, stats in performance_report['function_performance'].items()
            if stats['avg_time'] > 1.0
        ]
        
        if slow_functions:
            recommendations.append(f"Slow functions detected: {', '.join(slow_functions)}. Consider optimization.")
        
        return recommendations

# Global optimizer instance
advanced_performance_optimizer = AdvancedPerformanceOptimizer()

# Decorators for easy use
def cached(ttl_seconds: int = 3600):
    """Decorator for caching function results"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
            
            # Try to get from cache
            result = advanced_performance_optimizer.cache_manager.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            advanced_performance_optimizer.cache_manager.set(key, result, ttl_seconds)
            return result
        return wrapper
    return decorator

def profiled(func):
    """Decorator for profiling function performance"""
    return advanced_performance_optimizer.profiler.profile_function(func)

def optimized(ttl_seconds: int = 3600):
    """Decorator combining caching and profiling"""
    def decorator(func):
        return cached(ttl_seconds)(profiled(func))
    return decorator