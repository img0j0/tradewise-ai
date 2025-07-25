"""
Production configuration for TradeWise AI on Render
Optimized for performance, security, and monitoring
"""

import os
from datetime import timedelta

class ProductionConfig:
    """Production configuration class"""
    
    # Flask Core Settings
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SESSION_SECRET')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('SQLALCHEMY_POOL_SIZE', '10')),
        'pool_timeout': int(os.environ.get('SQLALCHEMY_POOL_TIMEOUT', '30')),
        'pool_recycle': int(os.environ.get('SQLALCHEMY_POOL_RECYCLE', '3600')),
        'pool_pre_ping': True,
        'echo': False  # Disable SQL query logging in production
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))
    
    # Session Configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Security Headers
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(days=365)
    
    # Payment Configuration
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Performance Settings
    COMPRESS_MIMETYPES = [
        'text/html', 'text/css', 'text/xml', 'application/json',
        'application/javascript', 'application/xml+rss',
        'application/atom+xml', 'image/svg+xml'
    ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
    
    # Worker Configuration
    WORKER_CONCURRENCY = int(os.environ.get('WORKER_CONCURRENCY', '4'))
    TASK_QUEUE_MAX_SIZE = int(os.environ.get('TASK_QUEUE_MAX_SIZE', '100'))
    PRECOMPUTATION_ENABLED = os.environ.get('PRECOMPUTATION_ENABLED', 'true').lower() == 'true'
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL')
    RATELIMIT_DEFAULT = "100/hour"
    
    # Monitoring Configuration
    PROMETHEUS_METRICS_ENABLED = True
    PERFORMANCE_MONITORING_ENABLED = True
    LOG_LEVEL = 'INFO'
    
    # External APIs
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    @staticmethod
    def validate_config():
        """Validate critical configuration values"""
        required_vars = [
            'SECRET_KEY', 'SQLALCHEMY_DATABASE_URI', 'REDIS_URL',
            'STRIPE_SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var.replace('SQLALCHEMY_DATABASE_URI', 'DATABASE_URL')):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Gunicorn Configuration
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = int(os.environ.get('WEB_CONCURRENCY', '2'))
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging Configuration
accesslog = '-'
errorlog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
loglevel = 'info'

def when_ready(server):
    """Called just after the server is started"""
    server.log.info("TradeWise AI server is ready. Workers: %s", workers)

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT"""
    worker.log.info("Worker %s interrupted", worker.pid)

def on_exit(server):
    """Called just before the master process is killed"""
    server.log.info("TradeWise AI server shutting down")