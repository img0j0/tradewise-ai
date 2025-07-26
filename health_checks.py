"""
Comprehensive Health Check System for TradeWise AI
Provides health monitoring for all external dependencies
"""

import os
import time
import logging
import requests
import psycopg2
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from flask import Blueprint, jsonify

# Redis imports with fallback
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Create health check blueprint
health_bp = Blueprint('health', __name__, url_prefix='/health')

class HealthChecker:
    """Comprehensive health checking for all services"""
    
    def __init__(self):
        self.timeout = int(os.getenv('HEALTH_CHECK_TIMEOUT', '10'))
        self.redis_enabled = os.getenv('REDIS_HEALTH_CHECK_ENABLED', 'true').lower() == 'true'
        self.db_enabled = os.getenv('DATABASE_HEALTH_CHECK_ENABLED', 'true').lower() == 'true'
        self.api_enabled = os.getenv('API_HEALTH_CHECK_ENABLED', 'true').lower() == 'true'
    
    def check_database(self) -> Dict[str, Any]:
        """Check PostgreSQL database connectivity"""
        start_time = time.time()
        
        try:
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                return {
                    'status': 'error',
                    'message': 'DATABASE_URL not configured',
                    'response_time_ms': 0
                }
            
            # Test database connection
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute('SELECT 1;')
            result = cursor.fetchone()
            
            # Test app-specific table (if exists)
            try:
                cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'user';")
                table_count = cursor.fetchone()[0]
                has_tables = table_count > 0
            except Exception:
                has_tables = False
            
            cursor.close()
            conn.close()
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                'status': 'healthy',
                'message': 'Database connection successful',
                'response_time_ms': response_time,
                'details': {
                    'connection_test': 'passed',
                    'query_test': 'passed',
                    'app_tables_present': has_tables,
                    'database_type': 'PostgreSQL'
                }
            }
            
        except psycopg2.OperationalError as e:
            return {
                'status': 'unhealthy',
                'message': f'Database connection failed: {str(e)}',
                'response_time_ms': round((time.time() - start_time) * 1000, 2),
                'error_type': 'connection_error'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Database health check error: {str(e)}',
                'response_time_ms': round((time.time() - start_time) * 1000, 2),
                'error_type': 'unexpected_error'
            }
    
    def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        start_time = time.time()
        
        if not REDIS_AVAILABLE:
            return {
                'status': 'disabled',
                'message': 'Redis client not available (using in-memory fallback)',
                'response_time_ms': 0
            }
        
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            
            # Test Redis connection
            client = redis.from_url(redis_url)
            
            # Test basic operations
            test_key = f"health_check_{int(time.time())}"
            client.set(test_key, "test_value", ex=60)
            value = client.get(test_key)
            client.delete(test_key)
            
            # Get Redis info
            info = client.info()
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                'status': 'healthy',
                'message': 'Redis connection successful',
                'response_time_ms': response_time,
                'details': {
                    'connection_test': 'passed',
                    'read_write_test': 'passed',
                    'redis_version': info.get('redis_version', 'unknown'),
                    'used_memory_human': info.get('used_memory_human', 'unknown'),
                    'connected_clients': info.get('connected_clients', 0)
                }
            }
            
        except redis.ConnectionError as e:
            return {
                'status': 'unhealthy',
                'message': f'Redis connection failed: {str(e)}',
                'response_time_ms': round((time.time() - start_time) * 1000, 2),
                'error_type': 'connection_error'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Redis health check error: {str(e)}',
                'response_time_ms': round((time.time() - start_time) * 1000, 2),
                'error_type': 'unexpected_error'
            }
    
    def check_external_apis(self) -> Dict[str, Any]:
        """Check external API connectivity"""
        start_time = time.time()
        api_results = {}
        
        # Check Yahoo Finance (primary market data source)
        try:
            yahoo_start = time.time()
            response = requests.get(
                'https://query1.finance.yahoo.com/v8/finance/chart/AAPL',
                timeout=self.timeout
            )
            yahoo_time = round((time.time() - yahoo_start) * 1000, 2)
            
            if response.status_code == 200:
                data = response.json()
                has_data = 'chart' in data and len(data['chart']['result']) > 0
                api_results['yahoo_finance'] = {
                    'status': 'healthy',
                    'response_time_ms': yahoo_time,
                    'data_available': has_data
                }
            else:
                api_results['yahoo_finance'] = {
                    'status': 'unhealthy',
                    'response_time_ms': yahoo_time,
                    'error': f'HTTP {response.status_code}'
                }
        except requests.exceptions.Timeout:
            api_results['yahoo_finance'] = {
                'status': 'unhealthy',
                'error': 'Timeout',
                'response_time_ms': self.timeout * 1000
            }
        except Exception as e:
            api_results['yahoo_finance'] = {
                'status': 'error',
                'error': str(e),
                'response_time_ms': round((time.time() - yahoo_start) * 1000, 2)
            }
        
        # Check Stripe API (if key provided)
        stripe_key = os.getenv('STRIPE_SECRET_KEY')
        if stripe_key and stripe_key.startswith(('sk_test_', 'sk_live_')):
            try:
                stripe_start = time.time()
                response = requests.get(
                    'https://api.stripe.com/v1/account',
                    headers={'Authorization': f'Bearer {stripe_key}'},
                    timeout=self.timeout
                )
                stripe_time = round((time.time() - stripe_start) * 1000, 2)
                
                if response.status_code == 200:
                    api_results['stripe'] = {
                        'status': 'healthy',
                        'response_time_ms': stripe_time,
                        'authenticated': True
                    }
                else:
                    api_results['stripe'] = {
                        'status': 'unhealthy',
                        'response_time_ms': stripe_time,
                        'error': f'HTTP {response.status_code}'
                    }
            except Exception as e:
                api_results['stripe'] = {
                    'status': 'error',
                    'error': str(e),
                    'response_time_ms': round((time.time() - stripe_start) * 1000, 2)
                }
        else:
            api_results['stripe'] = {
                'status': 'disabled',
                'message': 'Stripe API key not configured'
            }
        
        # Overall API status
        total_time = round((time.time() - start_time) * 1000, 2)
        healthy_apis = sum(1 for api in api_results.values() if api.get('status') == 'healthy')
        total_apis = len([api for api in api_results.values() if api.get('status') != 'disabled'])
        
        overall_status = 'healthy' if healthy_apis == total_apis and total_apis > 0 else 'degraded'
        
        return {
            'status': overall_status,
            'message': f'{healthy_apis}/{total_apis} APIs healthy',
            'response_time_ms': total_time,
            'apis': api_results
        }
    
    def comprehensive_health_check(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive status"""
        start_time = time.time()
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'services': {}
        }
        
        # Check database
        if self.db_enabled:
            results['services']['database'] = self.check_database()
        
        # Check Redis
        if self.redis_enabled:
            results['services']['redis'] = self.check_redis()
        
        # Check external APIs
        if self.api_enabled:
            results['services']['external_apis'] = self.check_external_apis()
        
        # Determine overall status
        service_statuses = []
        for service_name, service_data in results['services'].items():
            status = service_data.get('status', 'unknown')
            if status in ['unhealthy', 'error']:
                service_statuses.append('unhealthy')
            elif status == 'degraded':
                service_statuses.append('degraded')
            elif status == 'healthy':
                service_statuses.append('healthy')
        
        if 'unhealthy' in service_statuses:
            results['overall_status'] = 'unhealthy'
        elif 'degraded' in service_statuses:
            results['overall_status'] = 'degraded'
        else:
            results['overall_status'] = 'healthy'
        
        results['total_check_time_ms'] = round((time.time() - start_time) * 1000, 2)
        
        return results

# Initialize health checker
health_checker = HealthChecker()

@health_bp.route('/')
def health_overview():
    """Comprehensive health check endpoint"""
    try:
        health_data = health_checker.comprehensive_health_check()
        
        # Determine HTTP status code
        status_code = 200
        if health_data['overall_status'] == 'degraded':
            status_code = 206  # Partial Content
        elif health_data['overall_status'] == 'unhealthy':
            status_code = 503  # Service Unavailable
        
        return jsonify(health_data), status_code
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'error',
            'error': str(e)
        }), 500

@health_bp.route('/database')
def health_database():
    """Database-specific health check"""
    try:
        db_health = health_checker.check_database()
        status_code = 200 if db_health['status'] == 'healthy' else 503
        return jsonify(db_health), status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_bp.route('/redis')
def health_redis():
    """Redis-specific health check"""
    try:
        redis_health = health_checker.check_redis()
        status_code = 200 if redis_health['status'] in ['healthy', 'disabled'] else 503
        return jsonify(redis_health), status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_bp.route('/api')
def health_apis():
    """External APIs health check"""
    try:
        api_health = health_checker.check_external_apis()
        status_code = 200 if api_health['status'] in ['healthy', 'degraded'] else 503
        return jsonify(api_health), status_code
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_bp.route('/startup')
def health_startup():
    """Startup readiness check"""
    try:
        # Quick checks for startup readiness
        checks = {
            'environment_vars': True,  # Assume validated at startup
            'database': health_checker.check_database()['status'] == 'healthy',
            'redis': health_checker.check_redis()['status'] in ['healthy', 'disabled'],
            'external_apis': health_checker.check_external_apis()['status'] in ['healthy', 'degraded']
        }
        
        all_ready = all(checks.values())
        
        return jsonify({
            'ready': all_ready,
            'checks': checks,
            'timestamp': datetime.utcnow().isoformat()
        }), 200 if all_ready else 503
        
    except Exception as e:
        return jsonify({
            'ready': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500