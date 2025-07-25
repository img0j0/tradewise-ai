"""
Production Configuration for TradeWise AI
Security-hardened settings and environment validation
"""

import os
import sys
from datetime import timedelta

class ProductionConfig:
    """Production-ready configuration with security hardening"""
    
    # Core Flask Settings
    DEBUG = False
    TESTING = False
    
    # Secret Key Management
    SECRET_KEY = os.environ.get('SESSION_SECRET')
    if not SECRET_KEY:
        raise ValueError("SESSION_SECRET environment variable is required for production")
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is required for production")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20,
        'echo': False  # Disable SQL logging in production
    }
    
    # Session Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_NAME = 'tradewise_session'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_PATH = '/'
    
    # Security Headers
    PREFERRED_URL_SCHEME = 'https'
    
    # Cache Configuration
    CACHE_TYPE = 'simple'  # Upgrade to Redis in production
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_THRESHOLD = 1000
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'  # Upgrade to Redis
    
    # Stripe Configuration
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    if not STRIPE_SECRET_KEY:
        print("WARNING: STRIPE_SECRET_KEY not set - payment functionality disabled")
    
    # Performance Monitoring
    PERFORMANCE_MONITORING = True
    PERFORMANCE_LOG_FILE = 'performance.log'
    
    # Email Configuration (if needed)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

class DevelopmentConfig:
    """Development configuration with debugging enabled"""
    
    DEBUG = True
    TESTING = False
    
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-insecure')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///trading_platform.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'echo': True  # Enable SQL logging in development
    }
    
    # Session Security (relaxed for development)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'tradewise_dev_session'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Cache Configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 60  # Shorter cache for development
    
    # Stripe (test keys)
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

def get_config():
    """Get configuration based on environment"""
    if os.environ.get('REPLIT_DEPLOYMENT'):
        return ProductionConfig()
    else:
        return DevelopmentConfig()

def validate_environment():
    """Validate all required environment variables"""
    required_vars = []
    optional_vars = []
    
    if os.environ.get('REPLIT_DEPLOYMENT'):
        # Production requirements
        required_vars = [
            'SESSION_SECRET',
            'DATABASE_URL',
            'STRIPE_SECRET_KEY'
        ]
        optional_vars = [
            'MAIL_SERVER',
            'MAIL_USERNAME', 
            'MAIL_PASSWORD'
        ]
    else:
        # Development requirements
        required_vars = ['SESSION_SECRET']
        optional_vars = [
            'DATABASE_URL',
            'STRIPE_SECRET_KEY'
        ]
    
    # Check required variables
    missing_required = [var for var in required_vars if not os.environ.get(var)]
    if missing_required:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_required)}")
        sys.exit(1)
    
    # Check optional variables
    missing_optional = [var for var in optional_vars if not os.environ.get(var)]
    if missing_optional:
        print(f"WARNING: Missing optional environment variables: {', '.join(missing_optional)}")
    
    print("✅ Environment validation completed successfully")
    return True

# Auto-validate on import
if __name__ != '__main__':
    validate_environment()