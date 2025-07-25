"""
Database query optimization for TradeWise AI
Implements query optimization, indexing recommendations, and batch operations
"""

import logging
from sqlalchemy import text, inspect, Index
from app import db
from models import FavoriteStock, SearchHistory, StockAnalysis
from performance_monitor import performance_optimized
import time

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Database performance optimization utilities"""
    
    @staticmethod
    @performance_optimized()
    def analyze_query_performance():
        """Analyze database query performance and suggest optimizations"""
        recommendations = []
        
        try:
            # Check for missing indexes on frequently queried columns
            inspector = inspect(db.engine)
            
            # Analyze FavoriteStock queries
            fav_indexes = inspector.get_indexes('favorite_stock')
            existing_fav_indexes = {idx['column_names'][0] for idx in fav_indexes if len(idx['column_names']) == 1}
            
            if 'user_session' not in existing_fav_indexes:
                recommendations.append({
                    'type': 'missing_index',
                    'table': 'favorite_stock',
                    'column': 'user_session',
                    'reason': 'Frequently filtered by user session',
                    'query': 'CREATE INDEX idx_favorite_stock_user_session ON favorite_stock(user_session);'
                })
            
            if 'symbol' not in existing_fav_indexes:
                recommendations.append({
                    'type': 'missing_index',
                    'table': 'favorite_stock',
                    'column': 'symbol',
                    'reason': 'Frequently filtered by stock symbol',
                    'query': 'CREATE INDEX idx_favorite_stock_symbol ON favorite_stock(symbol);'
                })
            
            # Analyze SearchHistory queries
            search_indexes = inspector.get_indexes('search_history')
            existing_search_indexes = {idx['column_names'][0] for idx in search_indexes if len(idx['column_names']) == 1}
            
            if 'user_session' not in existing_search_indexes:
                recommendations.append({
                    'type': 'missing_index',
                    'table': 'search_history',
                    'column': 'user_session',
                    'reason': 'Frequently filtered by user session',
                    'query': 'CREATE INDEX idx_search_history_user_session ON search_history(user_session);'
                })
            
            # Compound index for timestamp + user_session queries
            compound_exists = any(
                set(idx['column_names']) == {'user_session', 'timestamp'} 
                for idx in search_indexes
            )
            
            if not compound_exists:
                recommendations.append({
                    'type': 'compound_index',
                    'table': 'search_history',
                    'columns': ['user_session', 'timestamp'],
                    'reason': 'Frequently queried together for recent searches',
                    'query': 'CREATE INDEX idx_search_history_session_time ON search_history(user_session, timestamp);'
                })
            
            return {
                'success': True,
                'recommendations': recommendations,
                'tables_analyzed': ['favorite_stock', 'search_history', 'stock_analysis']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing query performance: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommendations': []
            }
    
    @staticmethod
    @performance_optimized()
    def optimize_favorites_query(user_session, limit=10):
        """Optimized query for user favorites with reduced database calls"""
        try:
            start_time = time.time()
            
            # Single optimized query with proper ordering
            favorites = db.session.query(FavoriteStock)\
                .filter(FavoriteStock.user_session == user_session)\
                .order_by(FavoriteStock.timestamp.desc())\
                .limit(limit)\
                .all()
            
            query_time = (time.time() - start_time) * 1000
            
            # Convert to dict format efficiently
            result = [
                {
                    'id': fav.id,
                    'symbol': fav.symbol,
                    'company_name': fav.company_name,
                    'sector': fav.sector,
                    'timestamp': fav.timestamp.isoformat() if fav.timestamp else None
                }
                for fav in favorites
            ]
            
            logger.debug(f"Favorites query completed in {query_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Error in optimized favorites query: {e}")
            return []
    
    @staticmethod
    @performance_optimized()
    def optimize_search_history_query(user_session, limit=10):
        """Optimized query for search history with efficient ordering"""
        try:
            start_time = time.time()
            
            # Optimized query with proper indexing consideration
            searches = db.session.query(SearchHistory)\
                .filter(SearchHistory.user_session == user_session)\
                .order_by(SearchHistory.timestamp.desc())\
                .limit(limit)\
                .all()
            
            query_time = (time.time() - start_time) * 1000
            
            result = [
                {
                    'id': search.id,
                    'symbol': search.symbol,
                    'company_name': search.company_name,
                    'search_query': search.search_query,
                    'access_count': search.access_count,
                    'timestamp': search.timestamp.isoformat() if search.timestamp else None
                }
                for search in searches
            ]
            
            logger.debug(f"Search history query completed in {query_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Error in optimized search history query: {e}")
            return []
    
    @staticmethod
    @performance_optimized()
    def batch_insert_search_history(search_records):
        """Batch insert for multiple search history records"""
        try:
            if not search_records:
                return {'success': True, 'inserted': 0}
            
            start_time = time.time()
            
            # Use bulk insert for better performance
            db.session.bulk_insert_mappings(SearchHistory, search_records)
            db.session.commit()
            
            insert_time = (time.time() - start_time) * 1000
            logger.info(f"Batch inserted {len(search_records)} search records in {insert_time:.2f}ms")
            
            return {
                'success': True,
                'inserted': len(search_records),
                'time_ms': insert_time
            }
            
        except Exception as e:
            logger.error(f"Error in batch insert: {e}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'inserted': 0
            }
    
    @staticmethod
    def create_performance_indexes():
        """Create recommended performance indexes"""
        try:
            recommendations = DatabaseOptimizer.analyze_query_performance()
            applied_indexes = []
            
            if recommendations['success']:
                for rec in recommendations['recommendations']:
                    if rec['type'] in ['missing_index', 'compound_index']:
                        try:
                            db.session.execute(text(rec['query']))
                            applied_indexes.append(rec)
                            logger.info(f"Created index: {rec['query']}")
                        except Exception as e:
                            logger.warning(f"Index creation failed (may already exist): {e}")
                
                if applied_indexes:
                    db.session.commit()
            
            return {
                'success': True,
                'indexes_created': len(applied_indexes),
                'recommendations_applied': applied_indexes
            }
            
        except Exception as e:
            logger.error(f"Error creating performance indexes: {e}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'indexes_created': 0
            }

class QueryProfiler:
    """Profile database queries for performance analysis"""
    
    @staticmethod
    def profile_slow_queries():
        """Identify and profile slow database queries"""
        slow_queries = []
        
        try:
            # Test common query patterns and measure performance
            test_queries = [
                {
                    'name': 'user_favorites_query',
                    'query': lambda: db.session.query(FavoriteStock).filter_by(user_session='test').limit(10).all(),
                    'description': 'User favorites lookup'
                },
                {
                    'name': 'recent_searches_query', 
                    'query': lambda: db.session.query(SearchHistory).filter_by(user_session='test').order_by(SearchHistory.timestamp.desc()).limit(10).all(),
                    'description': 'Recent searches lookup'
                },
                {
                    'name': 'symbol_search_history',
                    'query': lambda: db.session.query(SearchHistory).filter_by(symbol='AAPL').all(),
                    'description': 'Symbol-based search history'
                }
            ]
            
            for test in test_queries:
                start_time = time.time()
                try:
                    test['query']()
                    execution_time = (time.time() - start_time) * 1000
                    
                    if execution_time > 100:  # Flag queries > 100ms as slow
                        slow_queries.append({
                            'name': test['name'],
                            'description': test['description'],
                            'execution_time_ms': round(execution_time, 2),
                            'status': 'slow'
                        })
                    else:
                        slow_queries.append({
                            'name': test['name'],
                            'description': test['description'],
                            'execution_time_ms': round(execution_time, 2),
                            'status': 'fast'
                        })
                        
                except Exception as e:
                    slow_queries.append({
                        'name': test['name'],
                        'description': test['description'],
                        'execution_time_ms': 0,
                        'status': 'error',
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'queries_profiled': len(test_queries),
                'slow_queries': [q for q in slow_queries if q['status'] == 'slow'],
                'all_results': slow_queries
            }
            
        except Exception as e:
            logger.error(f"Error profiling queries: {e}")
            return {
                'success': False,
                'error': str(e),
                'slow_queries': []
            }

# Initialize optimizer instance
db_optimizer = DatabaseOptimizer()
query_profiler = QueryProfiler()