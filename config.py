
# Production Configuration
import os
from datetime import timedelta

class ProductionConfig:
    """Production configuration for App Store deployment"""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key')
    DEBUG = False
    TESTING = False
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://localhost/trading_app')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # Session configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Security configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # API rate limiting
    RATELIMIT_STORAGE_URL = 'redis://localhost:6379'
    RATELIMIT_DEFAULT = '100 per hour'
    
    # Logging configuration
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'app.log'
    
    # Performance configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = 'redis://localhost:6379'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # AI model configuration
    AI_MODEL_CACHE_TTL = 3600
    AI_PREDICTION_TIMEOUT = 10
    
    # External API configuration
    YAHOO_FINANCE_TIMEOUT = 5
    YAHOO_FINANCE_RETRIES = 3
    
    @staticmethod
    def init_app(app):
        """Initialize production configuration"""
        # Configure logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            file_handler = RotatingFileHandler(
                ProductionConfig.LOG_FILE,
                maxBytes=10240000,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Trading app startup')

# Development configuration
class DevelopmentConfig:
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SECRET_KEY = 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configuration selection
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
