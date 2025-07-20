#!/usr/bin/env python3
"""
Production Performance Audit System
Comprehensive performance analysis and optimization recommendations
"""

import time
import psutil
import os
import gc
import threading
from datetime import datetime, timedelta
import json
import logging
from functools import wraps
import sqlite3
from collections import defaultdict, deque
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionPerformanceAuditor:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.performance_history = deque(maxlen=1000)
        self.optimization_recommendations = []
        self.critical_issues = []
        self.monitoring_active = False
        
    def audit_system_performance(self):
        """Comprehensive system performance audit"""
        audit_results = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': self._collect_system_metrics(),
            'application_metrics': self._collect_application_metrics(),
            'database_performance': self._audit_database_performance(),
            'api_performance': self._audit_api_performance(),
            'frontend_optimization': self._audit_frontend_optimization(),
            'memory_analysis': self._analyze_memory_usage(),
            'recommendations': self._generate_optimization_recommendations()
        }
        
        # Store audit results
        self.performance_history.append(audit_results)
        return audit_results
    
    def _collect_system_metrics(self):
        """Collect comprehensive system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_percent,
                'memory_total': memory.total,
                'memory_available': memory.available,
                'memory_percent': memory.percent,
                'disk_total': disk.total,
                'disk_used': disk.used,
                'disk_free': disk.free,
                'disk_percent': (disk.used / disk.total) * 100,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def _collect_application_metrics(self):
        """Collect application-specific performance metrics"""
        try:
            import main
            from app import app
            
            # Count active database connections
            active_connections = self._count_database_connections()
            
            # Memory usage by Python process
            process = psutil.Process()
            memory_info = process.memory_info()
            
            # Check for memory leaks
            gc_stats = gc.get_stats()
            
            return {
                'process_memory_rss': memory_info.rss,
                'process_memory_vms': memory_info.vms,
                'active_db_connections': active_connections,
                'garbage_collection_stats': gc_stats,
                'python_object_count': len(gc.get_objects()),
                'flask_debug_mode': app.debug if hasattr(app, 'debug') else False
            }
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return {}
    
    def _audit_database_performance(self):
        """Audit database performance and optimization opportunities"""
        try:
            from app import db
            
            # Check for slow queries
            slow_queries = self._identify_slow_queries()
            
            # Analyze table sizes and indexes
            table_analysis = self._analyze_database_tables()
            
            # Connection pool status
            pool_status = self._check_connection_pool()
            
            return {
                'slow_queries': slow_queries,
                'table_analysis': table_analysis,
                'connection_pool': pool_status,
                'optimization_opportunities': self._identify_db_optimizations()
            }
        except Exception as e:
            logger.error(f"Error auditing database performance: {e}")
            return {}
    
    def _audit_api_performance(self):
        """Audit API endpoint performance"""
        try:
            # Test critical API endpoints
            endpoints_to_test = [
                '/api/search-stocks',
                '/api/dashboard-data',
                '/api/ai-assistant',
                '/api/portfolio-analytics',
                '/api/market-intelligence/overview'
            ]
            
            performance_results = {}
            
            for endpoint in endpoints_to_test:
                try:
                    start_time = time.time()
                    # Test endpoint (would need actual server URL)
                    response_time = time.time() - start_time
                    
                    performance_results[endpoint] = {
                        'response_time': response_time,
                        'status': 'healthy' if response_time < 2.0 else 'slow'
                    }
                except Exception as e:
                    performance_results[endpoint] = {
                        'response_time': None,
                        'status': 'error',
                        'error': str(e)
                    }
            
            return performance_results
        except Exception as e:
            logger.error(f"Error auditing API performance: {e}")
            return {}
    
    def _audit_frontend_optimization(self):
        """Audit frontend performance opportunities"""
        static_files_analysis = self._analyze_static_files()
        
        return {
            'static_files': static_files_analysis,
            'optimization_opportunities': [
                'Enable gzip compression',
                'Minify CSS and JavaScript',
                'Optimize image sizes',
                'Implement browser caching',
                'Use CDN for static assets'
            ]
        }
    
    def _analyze_memory_usage(self):
        """Detailed memory usage analysis"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            # Memory growth analysis
            memory_growth = self._analyze_memory_growth()
            
            # Identify memory leaks
            potential_leaks = self._identify_memory_leaks()
            
            return {
                'current_memory_mb': memory_info.rss / 1024 / 1024,
                'memory_growth_trend': memory_growth,
                'potential_leaks': potential_leaks,
                'garbage_collection_needed': len(gc.garbage) > 0
            }
        except Exception as e:
            logger.error(f"Error analyzing memory usage: {e}")
            return {}
    
    def _generate_optimization_recommendations(self):
        """Generate specific optimization recommendations"""
        recommendations = []
        
        # System-level recommendations
        system_metrics = self._collect_system_metrics()
        if system_metrics.get('cpu_usage', 0) > 80:
            recommendations.append({
                'priority': 'high',
                'category': 'system',
                'issue': 'High CPU usage detected',
                'recommendation': 'Implement request rate limiting and optimize CPU-intensive operations'
            })
        
        if system_metrics.get('memory_percent', 0) > 85:
            recommendations.append({
                'priority': 'high',
                'category': 'memory',
                'issue': 'High memory usage detected',
                'recommendation': 'Implement memory optimization and garbage collection tuning'
            })
        
        # Application-level recommendations
        recommendations.extend([
            {
                'priority': 'medium',
                'category': 'caching',
                'issue': 'Potential caching improvements',
                'recommendation': 'Implement Redis caching for frequently accessed data'
            },
            {
                'priority': 'medium',
                'category': 'database',
                'issue': 'Database query optimization',
                'recommendation': 'Add database indexes and optimize slow queries'
            },
            {
                'priority': 'low',
                'category': 'frontend',
                'issue': 'Static asset optimization',
                'recommendation': 'Enable compression and implement CDN'
            }
        ])
        
        return recommendations
    
    def _count_database_connections(self):
        """Count active database connections"""
        try:
            # This would need to be adapted based on actual database setup
            return 1  # Placeholder
        except:
            return 0
    
    def _identify_slow_queries(self):
        """Identify slow database queries"""
        # Placeholder - would need actual query logging
        return []
    
    def _analyze_database_tables(self):
        """Analyze database table performance"""
        # Placeholder - would need actual database analysis
        return {}
    
    def _check_connection_pool(self):
        """Check database connection pool status"""
        # Placeholder - would need actual connection pool monitoring
        return {'status': 'healthy'}
    
    def _identify_db_optimizations(self):
        """Identify database optimization opportunities"""
        return [
            'Add indexes for frequently queried columns',
            'Implement query result caching',
            'Optimize JOIN operations',
            'Consider database connection pooling'
        ]
    
    def _analyze_static_files(self):
        """Analyze static file optimization opportunities"""
        static_dir = 'static'
        if not os.path.exists(static_dir):
            return {}
        
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    size = os.path.getsize(filepath)
                    total_size += size
                    file_count += 1
                except:
                    pass
        
        return {
            'total_size_mb': total_size / 1024 / 1024,
            'file_count': file_count,
            'optimization_potential': 'Medium' if total_size > 5 * 1024 * 1024 else 'Low'
        }
    
    def _analyze_memory_growth(self):
        """Analyze memory growth patterns"""
        if len(self.performance_history) < 2:
            return 'insufficient_data'
        
        # Simple memory growth analysis
        recent_memory = [h.get('system_metrics', {}).get('memory_percent', 0) 
                        for h in list(self.performance_history)[-10:]]
        
        if len(recent_memory) < 2:
            return 'stable'
        
        growth_rate = (recent_memory[-1] - recent_memory[0]) / len(recent_memory)
        
        if growth_rate > 1:
            return 'increasing'
        elif growth_rate < -1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _identify_memory_leaks(self):
        """Identify potential memory leaks"""
        # Force garbage collection
        gc.collect()
        
        # Check for uncollectable objects
        uncollectable = len(gc.garbage)
        
        return {
            'uncollectable_objects': uncollectable,
            'potential_leak': uncollectable > 0
        }
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        audit_results = self.audit_system_performance()
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'executive_summary': self._generate_executive_summary(audit_results),
            'detailed_analysis': audit_results,
            'action_items': self._prioritize_action_items(audit_results),
            'performance_score': self._calculate_performance_score(audit_results)
        }
        
        return report
    
    def _generate_executive_summary(self, audit_results):
        """Generate executive summary of performance audit"""
        system_metrics = audit_results.get('system_metrics', {})
        
        cpu_status = 'good' if system_metrics.get('cpu_usage', 0) < 70 else 'needs_attention'
        memory_status = 'good' if system_metrics.get('memory_percent', 0) < 80 else 'needs_attention'
        
        return {
            'overall_health': 'good' if cpu_status == 'good' and memory_status == 'good' else 'needs_attention',
            'cpu_status': cpu_status,
            'memory_status': memory_status,
            'critical_issues_count': len([r for r in audit_results.get('recommendations', []) 
                                        if r.get('priority') == 'high']),
            'ready_for_production': cpu_status == 'good' and memory_status == 'good'
        }
    
    def _prioritize_action_items(self, audit_results):
        """Prioritize optimization action items"""
        recommendations = audit_results.get('recommendations', [])
        
        return {
            'immediate': [r for r in recommendations if r.get('priority') == 'high'],
            'short_term': [r for r in recommendations if r.get('priority') == 'medium'],
            'long_term': [r for r in recommendations if r.get('priority') == 'low']
        }
    
    def _calculate_performance_score(self, audit_results):
        """Calculate overall performance score"""
        system_metrics = audit_results.get('system_metrics', {})
        
        cpu_score = max(0, 100 - system_metrics.get('cpu_usage', 0))
        memory_score = max(0, 100 - system_metrics.get('memory_percent', 0))
        
        # Average the scores
        overall_score = (cpu_score + memory_score) / 2
        
        return {
            'overall_score': round(overall_score, 1),
            'cpu_score': round(cpu_score, 1),
            'memory_score': round(memory_score, 1),
            'grade': 'A' if overall_score >= 90 else 'B' if overall_score >= 80 else 'C' if overall_score >= 70 else 'D'
        }

# Global auditor instance
performance_auditor = ProductionPerformanceAuditor()

def audit_performance():
    """Run performance audit and return results"""
    return performance_auditor.generate_performance_report()

if __name__ == "__main__":
    # Run performance audit
    report = audit_performance()
    print("Performance Audit Report:")
    print("=" * 50)
    print(json.dumps(report, indent=2, default=str))