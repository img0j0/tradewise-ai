
# Security Enhancement Module
from flask import request, abort
import hashlib
import hmac
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class SecurityEnhancer:
    """Security enhancements for production deployment"""
    
    @staticmethod
    def validate_request_signature(secret_key):
        """Validate request signatures for API security"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Skip validation for development
                if not secret_key:
                    return f(*args, **kwargs)
                
                signature = request.headers.get('X-Signature')
                if not signature:
                    abort(401, 'Missing signature')
                
                # Validate signature
                payload = request.get_data()
                expected_signature = hmac.new(
                    secret_key.encode(),
                    payload,
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(signature, expected_signature):
                    abort(401, 'Invalid signature')
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @staticmethod
    def sanitize_input(data):
        """Sanitize user input to prevent injection attacks"""
        if isinstance(data, str):
            # Remove potentially dangerous characters
            dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}']
            for char in dangerous_chars:
                data = data.replace(char, '')
        return data
    
    @staticmethod
    def add_security_headers():
        """Add security headers to all responses"""
        from routes import app
        
        @app.after_request
        def add_security_headers(response):
            # Add security headers
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'"
            
            return response
        
        logger.info("Security headers added")

# Initialize security enhancements
if __name__ == "__main__":
    SecurityEnhancer.add_security_headers()
