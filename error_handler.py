"""
Centralized Error Handler for TradeWise AI
Provides unified error handling, logging, and user-friendly error responses
"""

import logging
import traceback
import os
import requests
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, Union
from flask import Flask, request, jsonify, Response
from werkzeug.exceptions import HTTPException
import json

# Configure logging
def setup_logging():
    """Setup centralized logging configuration"""
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(logs_dir, 'app.log')),
            logging.StreamHandler()
        ]
    )
    
    # Configure rotating log handlers
    from logging.handlers import RotatingFileHandler
    
    # App log handler
    app_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'app.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    app_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Worker log handler
    worker_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'worker.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    worker_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Error log handler for critical failures
    error_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'errors.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(pathname)s:%(lineno)d\n%(stack_info)s\n'
    ))
    
    # Add handlers to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    
    # Setup specific loggers
    worker_logger = logging.getLogger('worker')
    worker_logger.addHandler(worker_handler)
    
    return logging.getLogger(__name__)

# Error categories and user-friendly messages
ERROR_MESSAGES = {
    'API_KEY_MISSING': {
        'message': 'API key is missing or invalid',
        'action': 'Please check your API key configuration',
        'code': 'API_001'
    },
    'API_RATE_LIMIT': {
        'message': 'API rate limit exceeded',
        'action': 'Please try again in a few minutes',
        'code': 'API_002'
    },
    'API_TIMEOUT': {
        'message': 'External API request timed out',
        'action': 'Please try again later',
        'code': 'API_003'
    },
    'DATA_NOT_FOUND': {
        'message': 'Requested data not found',
        'action': 'Please verify the symbol or try a different search',
        'code': 'DATA_001'
    },
    'INVALID_INPUT': {
        'message': 'Invalid input provided',
        'action': 'Please check your input and try again',
        'code': 'INPUT_001'
    },
    'DATABASE_ERROR': {
        'message': 'Database operation failed',
        'action': 'Please try again later',
        'code': 'DB_001'
    },
    'REDIS_ERROR': {
        'message': 'Cache service unavailable',
        'action': 'System will continue with reduced performance',
        'code': 'CACHE_001'
    },
    'WORKER_ERROR': {
        'message': 'Background processing failed',
        'action': 'Please try again or contact support',
        'code': 'WORKER_001'
    },
    'PREMIUM_REQUIRED': {
        'message': 'Premium subscription required',
        'action': 'Please upgrade to access this feature',
        'code': 'PREMIUM_001'
    },
    'SYSTEM_ERROR': {
        'message': 'An unexpected error occurred',
        'action': 'Please try again later or contact support',
        'code': 'SYS_001'
    }
}

class TradeWiseError(Exception):
    """Base exception class for TradeWise AI errors"""
    def __init__(self, error_type: str, details: str = None, original_error: Exception = None):
        self.error_type = error_type
        self.details = details
        self.original_error = original_error
        self.timestamp = datetime.utcnow()
        super().__init__(self.get_message())
    
    def get_message(self) -> str:
        """Get user-friendly error message"""
        error_info = ERROR_MESSAGES.get(self.error_type, ERROR_MESSAGES['SYSTEM_ERROR'])
        return error_info['message']
    
    def get_error_response(self) -> Dict[str, Any]:
        """Get structured error response for API"""
        error_info = ERROR_MESSAGES.get(self.error_type, ERROR_MESSAGES['SYSTEM_ERROR'])
        return {
            'status': 'failed',
            'error': {
                'code': error_info['code'],
                'message': error_info['message'],
                'action': error_info['action'],
                'details': self.details,
                'timestamp': self.timestamp.isoformat()
            }
        }

class ErrorHandler:
    """Centralized error handler for TradeWise AI"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.notification_enabled = os.getenv('ERROR_NOTIFICATIONS_ENABLED', 'false').lower() == 'true'
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize error handler with Flask app"""
        self.app = app
        
        # Register error handlers
        app.register_error_handler(TradeWiseError, self.handle_tradewise_error)
        app.register_error_handler(HTTPException, self.handle_http_error)
        app.register_error_handler(Exception, self.handle_generic_error)
        
        # Add before/after request handlers for logging
        app.before_request(self.log_request)
        app.after_request(self.log_response)
    
    def log_request(self):
        """Log incoming requests"""
        self.logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
    
    def log_response(self, response):
        """Log outgoing responses"""
        if response.status_code >= 400:
            self.logger.warning(f"Response: {response.status_code} for {request.method} {request.path}")
        return response
    
    def handle_tradewise_error(self, error: TradeWiseError) -> Tuple[Response, int]:
        """Handle custom TradeWise errors"""
        self.logger.error(f"TradeWise Error: {error.error_type} - {error.details or 'No details'}")
        
        if error.original_error:
            self.logger.error(f"Original error: {str(error.original_error)}")
            self.logger.error(traceback.format_exc())
        
        # Send notification for critical errors
        if error.error_type in ['DATABASE_ERROR', 'REDIS_ERROR', 'SYSTEM_ERROR']:
            self.send_critical_error_notification(error.original_error or error)
        
        return jsonify(error.get_error_response()), 400
    
    def handle_http_error(self, error: HTTPException) -> Tuple[Response, int]:
        """Handle HTTP errors"""
        self.logger.warning(f"HTTP Error: {error.code} - {error.description}")
        
        return jsonify({
            'status': 'failed',
            'error': {
                'code': f'HTTP_{error.code}',
                'message': error.description or 'HTTP error occurred',
                'action': 'Please try again or contact support',
                'timestamp': datetime.utcnow().isoformat()
            }
        }), error.code or 500
    
    def handle_generic_error(self, error: Exception) -> Tuple[Response, int]:
        """Handle unexpected errors"""
        self.logger.error(f"Unexpected error: {str(error)}")
        self.logger.error(traceback.format_exc())
        
        # Send critical error notification
        self.send_critical_error_notification(error)
        
        return jsonify({
            'status': 'failed',
            'error': {
                'code': 'SYS_001',
                'message': 'An unexpected error occurred',
                'action': 'Please try again later or contact support',
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 500
    
    def send_critical_error_notification(self, error: Exception):
        """Send notification for critical errors"""
        if not self.notification_enabled:
            return
        
        try:
            # Slack notification (if configured)
            slack_webhook = os.getenv('SLACK_ERROR_WEBHOOK')
            if slack_webhook:
                self._send_slack_notification(error, slack_webhook)
            
            # Email notification (if configured)
            email_config = {
                'smtp_server': os.getenv('SMTP_SERVER'),
                'smtp_port': os.getenv('SMTP_PORT'),
                'smtp_user': os.getenv('SMTP_USER'),
                'smtp_password': os.getenv('SMTP_PASSWORD'),
                'error_email': os.getenv('ERROR_EMAIL')
            }
            if all(email_config.values()):
                self._send_email_notification(error, email_config)
                
        except Exception as notification_error:
            self.logger.error(f"Failed to send error notification: {notification_error}")
    
    def _send_slack_notification(self, error: Exception, webhook_url: str):
        """Send Slack notification for critical errors"""
        message = {
            "text": f"🚨 TradeWise AI Critical Error",
            "attachments": [
                {
                    "color": "danger",
                    "fields": [
                        {
                            "title": "Error Type",
                            "value": str(type(error).__name__),
                            "short": True
                        },
                        {
                            "title": "Message",
                            "value": str(error),
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": datetime.utcnow().isoformat(),
                            "short": True
                        }
                    ]
                }
            ]
        }
        
        requests.post(webhook_url, json=message, timeout=10)
    
    def _send_email_notification(self, error: Exception, email_config: Dict):
        """Send email notification for critical errors"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = email_config['smtp_user']
        msg['To'] = email_config['error_email']
        msg['Subject'] = 'TradeWise AI Critical Error Alert'
        
        body = f"""
        Critical Error in TradeWise AI
        
        Error Type: {type(error).__name__}
        Message: {str(error)}
        Timestamp: {datetime.utcnow().isoformat()}
        
        Stack Trace:
        {traceback.format_exc()}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['smtp_user'], email_config['smtp_password'])
        server.send_message(msg)
        server.quit()

# Utility functions for consistent error handling
def handle_api_error(func):
    """Decorator for handling API-related errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.Timeout:
            raise TradeWiseError('API_TIMEOUT', 'External API request timed out')
        except requests.exceptions.HTTPError as e:
            if hasattr(e, 'response') and e.response.status_code == 429:
                raise TradeWiseError('API_RATE_LIMIT', 'API rate limit exceeded')
            elif hasattr(e, 'response') and e.response.status_code == 401:
                raise TradeWiseError('API_KEY_MISSING', 'API authentication failed')
            else:
                raise TradeWiseError('SYSTEM_ERROR', f'API error: {str(e)}', e)
        except Exception as e:
            raise TradeWiseError('SYSTEM_ERROR', f'Unexpected API error: {str(e)}', e)
    
    return wrapper

def handle_database_error(func):
    """Decorator for handling database-related errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if 'connection' in str(e).lower():
                raise TradeWiseError('DATABASE_ERROR', 'Database connection failed', e)
            else:
                raise TradeWiseError('DATABASE_ERROR', f'Database operation failed: {str(e)}', e)
    
    return wrapper

def handle_redis_error(func):
    """Decorator for handling Redis-related errors"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise TradeWiseError('REDIS_ERROR', 'Cache service unavailable', e)
    
    return wrapper

# Initialize logging on import
logger = setup_logging()