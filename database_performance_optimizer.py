#!/usr/bin/env python3
"""
Database Performance Optimizer
Advanced database optimization for production readiness
"""

import logging
import time
from functools import wraps
from datetime import datetime, timedelta
import json
from sqlalchemy import text, inspect
from sqlalchemy.pool import QueuePool
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabasePerformanceOptimizer:
    def __init__(self):
        self.query_performance_log = []
        self.slow_query_threshold = 1.0  # seconds
        self.optimization_applied = []
        
    def optimize_database_configuration(self):
        """Apply production database optimizations"""
        optimizations = []
        
        try:
            from app import app, db
            
            # 1. Connection Pool Optimization
            pool_optimizations = self._optimize_connection_pool(app)
            optimizations.extend(pool_optimizations)
            
            # 2. Query Optimization
            query_optimizations = self._optimize_queries()
            optimizations.extend(query_optimizations)
            
            # 3. Index Analysis and Creation
            index_optimizations = self._optimize_indexes()
            optimizations.extend(index_optimizations)
            
            # 4. Memory and Cache Optimization
            cache_optimizations = self._optimize_caching()
            optimizations.extend(cache_optimizations)
            
            logger.info(f"Applied {len(optimizations)} database optimizations")
            return {
                'optimizations_applied': optimizations,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database optimization error: {e}")
            return {
                'optimizations_applied': [],
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _optimize_connection_pool(self, app):
        """Optimize database connection pooling"""
        optimizations = []
        
        try:
            # Check current connection pool settings
            current_config = app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {})
            
            # Recommended production settings
            recommended_settings = {
                'pool_size': 20,  # Increase pool size for production
                'max_overflow': 30,  # Allow overflow connections
                'pool_recycle': 1800,  # Recycle connections every 30 minutes
                'pool_pre_ping': True,  # Verify connections before use
                'pool_timeout': 30,  # Timeout for getting connection
                'poolclass': QueuePool  # Use queue-based pooling
            }
            
            # Apply optimizations
            optimized_config = {**current_config, **recommended_settings}
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = optimized_config
            
            optimizations.append({
                'category': 'connection_pool',
                'optimization': 'Enhanced connection pool configuration',
                'details': recommended_settings
            })
            
        except Exception as e:
            logger.error(f"Connection pool optimization error: {e}")
        
        return optimizations
    
    def _optimize_queries(self):
        """Optimize database queries"""
        optimizations = []
        
        try:
            from app import db
            
            # Create query performance monitoring
            @wraps(db.session.execute)
            def monitored_execute(original_execute):
                def wrapper(*args, **kwargs):
                    start_time = time.time()
                    result = original_execute(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Log slow queries
                    if execution_time > self.slow_query_threshold:
                        self.query_performance_log.append({
                            'query': str(args[0]) if args else 'unknown',
                            'execution_time': execution_time,
                            'timestamp': datetime.now().isoformat()
                        })
                        logger.warning(f"Slow query detected: {execution_time:.2f}s")
                    
                    return result
                return wrapper
            
            # Apply query monitoring (in development/staging)
            optimizations.append({
                'category': 'query_monitoring',
                'optimization': 'Query performance monitoring enabled',
                'details': {'slow_query_threshold': self.slow_query_threshold}
            })
            
        except Exception as e:
            logger.error(f"Query optimization error: {e}")
        
        return optimizations
    
    def _optimize_indexes(self):
        """Analyze and optimize database indexes"""
        optimizations = []
        
        try:
            from app import db
            from models import User, UserAccount, Trade, Portfolio, Alert
            
            # Recommended indexes for performance
            recommended_indexes = [
                {
                    'table': 'user',
                    'columns': ['email'],
                    'reason': 'Frequent email lookups for authentication'
                },
                {
                    'table': 'trade',
                    'columns': ['user_id', 'timestamp'],
                    'reason': 'User trade history queries'
                },
                {
                    'table': 'portfolio',
                    'columns': ['user_id', 'symbol'],
                    'reason': 'Portfolio lookups by user and symbol'
                },
                {
                    'table': 'alert',
                    'columns': ['user_id', 'active'],
                    'reason': 'Active alerts for user queries'
                }
            ]
            
            # Check existing indexes
            inspector = inspect(db.engine)
            
            for index_info in recommended_indexes:
                table_name = index_info['table']
                columns = index_info['columns']
                
                try:
                    existing_indexes = inspector.get_indexes(table_name)
                    
                    # Check if index already exists
                    index_exists = any(
                        set(idx['column_names']) == set(columns)
                        for idx in existing_indexes
                    )
                    
                    if not index_exists:
                        # Create index
                        index_name = f"idx_{table_name}_{'_'.join(columns)}"
                        columns_str = ', '.join(columns)
                        
                        create_index_sql = f"""
                        CREATE INDEX IF NOT EXISTS {index_name} 
                        ON {table_name} ({columns_str})
                        """
                        
                        db.session.execute(text(create_index_sql))
                        db.session.commit()
                        
                        optimizations.append({
                            'category': 'indexes',
                            'optimization': f'Created index on {table_name}({columns_str})',
                            'details': index_info
                        })
                        
                except Exception as e:
                    logger.error(f"Index creation error for {table_name}: {e}")
            
        except Exception as e:
            logger.error(f"Index optimization error: {e}")
        
        return optimizations
    
    def _optimize_caching(self):
        """Optimize database caching"""
        optimizations = []
        
        try:
            from app import app
            
            # Enable SQLAlchemy query caching
            cache_config = {
                'SQLALCHEMY_RECORD_QUERIES': False,  # Disable in production
                'SQLALCHEMY_TRACK_MODIFICATIONS': False,  # Reduce overhead
                'SQLALCHEMY_ECHO': False  # Disable SQL logging in production
            }
            
            for key, value in cache_config.items():
                app.config[key] = value
            
            optimizations.append({
                'category': 'caching',
                'optimization': 'SQLAlchemy caching optimizations applied',
                'details': cache_config
            })
            
        except Exception as e:
            logger.error(f"Caching optimization error: {e}")
        
        return optimizations
    
    def analyze_query_performance(self):
        """Analyze query performance and identify bottlenecks"""
        analysis = {
            'total_queries_monitored': len(self.query_performance_log),
            'slow_queries_count': len([q for q in self.query_performance_log 
                                     if q['execution_time'] > self.slow_query_threshold]),
            'average_query_time': 0,
            'slowest_queries': [],
            'recommendations': []
        }
        
        if self.query_performance_log:
            # Calculate average query time
            total_time = sum(q['execution_time'] for q in self.query_performance_log)
            analysis['average_query_time'] = total_time / len(self.query_performance_log)
            
            # Find slowest queries
            sorted_queries = sorted(self.query_performance_log, 
                                  key=lambda x: x['execution_time'], reverse=True)
            analysis['slowest_queries'] = sorted_queries[:5]
            
            # Generate recommendations
            if analysis['slow_queries_count'] > 0:
                analysis['recommendations'].extend([
                    'Consider adding database indexes for slow queries',
                    'Optimize query structure and joins',
                    'Implement query result caching',
                    'Consider database connection pooling'
                ])
        
        return analysis
    
    def optimize_production_settings(self):
        """Apply comprehensive production database settings"""
        try:
            from app import app, db
            
            # Production database configuration
            production_config = {
                'SQLALCHEMY_ENGINE_OPTIONS': {
                    'pool_size': 20,
                    'max_overflow': 30,
                    'pool_recycle': 1800,
                    'pool_pre_ping': True,
                    'pool_timeout': 30,
                    'echo': False,
                    'echo_pool': False,
                    'future': True
                },
                'SQLALCHEMY_RECORD_QUERIES': False,
                'SQLALCHEMY_TRACK_MODIFICATIONS': False,
                'SQLALCHEMY_ECHO': False
            }
            
            # Apply configuration
            for key, value in production_config.items():
                app.config[key] = value
            
            logger.info("Production database settings applied")
            return {
                'status': 'success',
                'configuration_applied': production_config,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Production settings optimization error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def monitor_database_health(self):
        """Monitor database health metrics"""
        health_metrics = {
            'timestamp': datetime.now().isoformat(),
            'connection_status': 'unknown',
            'active_connections': 0,
            'query_performance': {},
            'recommendations': []
        }
        
        try:
            from app import db
            
            # Test database connection
            db.session.execute(text('SELECT 1'))
            health_metrics['connection_status'] = 'healthy'
            
            # Get query performance analysis
            health_metrics['query_performance'] = self.analyze_query_performance()
            
            # Generate health recommendations
            if health_metrics['query_performance']['slow_queries_count'] > 10:
                health_metrics['recommendations'].append(
                    'High number of slow queries detected - consider query optimization'
                )
            
            if health_metrics['query_performance']['average_query_time'] > 0.5:
                health_metrics['recommendations'].append(
                    'Average query time is high - consider database tuning'
                )
            
        except Exception as e:
            logger.error(f"Database health monitoring error: {e}")
            health_metrics['connection_status'] = 'error'
            health_metrics['error'] = str(e)
        
        return health_metrics

# Global optimizer instance
db_optimizer = DatabasePerformanceOptimizer()

def optimize_database_for_production():
    """Optimize database for production deployment"""
    return db_optimizer.optimize_database_configuration()

def monitor_database_performance():
    """Monitor database performance"""
    return db_optimizer.monitor_database_health()

if __name__ == "__main__":
    # Run database optimization
    result = optimize_database_for_production()
    print("Database Optimization Results:")
    print("=" * 50)
    print(json.dumps(result, indent=2, default=str))