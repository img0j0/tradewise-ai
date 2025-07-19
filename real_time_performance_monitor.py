"""
Real-Time Performance Monitor
Live performance tracking and optimization dashboard
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import deque, defaultdict
import logging
from advanced_performance_optimizer import advanced_performance_optimizer

class RealTimePerformanceMonitor:
    """Real-time performance monitoring system"""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.performance_data = deque(maxlen=max_samples)
        self.api_response_times = defaultdict(lambda: deque(maxlen=100))
        self.active_users = set()
        self.error_counts = defaultdict(int)
        self.logger = logging.getLogger(__name__)
        
        # Start monitoring thread
        self._start_monitoring()
        
    def _start_monitoring(self):
        """Start background monitoring thread"""
        def monitor_loop():
            while True:
                try:
                    self._collect_metrics()
                    time.sleep(5)  # Collect every 5 seconds
                except Exception as e:
                    self.logger.error(f"Monitor error: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        self.logger.info("Real-time performance monitor started")
    
    def _collect_metrics(self):
        """Collect current performance metrics"""
        try:
            import psutil
            process = psutil.Process()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'active_users': len(self.active_users),
                'cache_hits': advanced_performance_optimizer.cache_manager.cache_stats['hits'],
                'cache_misses': advanced_performance_optimizer.cache_manager.cache_stats['misses'],
                'total_errors': sum(self.error_counts.values())
            }
            
            self.performance_data.append(metrics)
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
    
    def track_api_call(self, endpoint: str, response_time: float, status_code: int):
        """Track API call performance"""
        self.api_response_times[endpoint].append({
            'time': response_time,
            'status': status_code,
            'timestamp': datetime.now()
        })
        
        if status_code >= 400:
            self.error_counts[endpoint] += 1
    
    def track_user_activity(self, user_id: str, action: str):
        """Track user activity"""
        if action == 'login':
            self.active_users.add(user_id)
        elif action == 'logout':
            self.active_users.discard(user_id)
    
    def get_live_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        if not self.performance_data:
            return {'error': 'No performance data available'}
        
        # Get recent data
        recent_data = list(self.performance_data)[-60:]  # Last 5 minutes
        
        # Calculate averages
        avg_cpu = sum(d['cpu_percent'] for d in recent_data) / len(recent_data)
        avg_memory = sum(d['memory_mb'] for d in recent_data) / len(recent_data)
        current_users = len(self.active_users)
        
        # API performance
        api_stats = {}
        for endpoint, times in self.api_response_times.items():
            if times:
                recent_times = [t['time'] for t in times if (datetime.now() - t['timestamp']).seconds < 300]
                if recent_times:
                    api_stats[endpoint] = {
                        'avg_response_time': sum(recent_times) / len(recent_times),
                        'max_response_time': max(recent_times),
                        'call_count': len(recent_times)
                    }
        
        # Get optimization recommendations
        optimization_report = advanced_performance_optimizer.get_optimization_report()
        
        return {
            'system_metrics': {
                'cpu_percent': recent_data[-1]['cpu_percent'] if recent_data else 0,
                'memory_mb': recent_data[-1]['memory_mb'] if recent_data else 0,
                'avg_cpu_5min': avg_cpu,
                'avg_memory_5min': avg_memory,
                'active_users': current_users
            },
            'api_performance': api_stats,
            'cache_performance': {
                'hit_rate': self._calculate_cache_hit_rate(),
                'total_hits': advanced_performance_optimizer.cache_manager.cache_stats['hits'],
                'total_misses': advanced_performance_optimizer.cache_manager.cache_stats['misses']
            },
            'error_summary': dict(self.error_counts),
            'optimization_recommendations': optimization_report.get('recommendations', []),
            'performance_trend': self._calculate_performance_trend(),
            'last_updated': datetime.now().isoformat()
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        stats = advanced_performance_optimizer.cache_manager.cache_stats
        total = stats['hits'] + stats['misses']
        return (stats['hits'] / total * 100) if total > 0 else 0
    
    def _calculate_performance_trend(self) -> str:
        """Calculate overall performance trend"""
        if len(self.performance_data) < 10:
            return 'stable'
        
        recent = list(self.performance_data)[-10:]
        cpu_trend = (recent[-1]['cpu_percent'] - recent[0]['cpu_percent']) / 10
        memory_trend = (recent[-1]['memory_mb'] - recent[0]['memory_mb']) / 10
        
        if cpu_trend > 2 or memory_trend > 10:
            return 'degrading'
        elif cpu_trend < -2 and memory_trend < -10:
            return 'improving'
        else:
            return 'stable'

# Global performance monitor
performance_monitor = RealTimePerformanceMonitor()

def track_performance(endpoint: str):
    """Decorator to track API endpoint performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                status_code = 200
                return result
            except Exception as e:
                status_code = 500
                raise
            finally:
                response_time = time.time() - start_time
                performance_monitor.track_api_call(endpoint, response_time, status_code)
        return wrapper
    return decorator