
# API Enhancement Module
from functools import wraps
import time
import logging
from flask import request, jsonify
import traceback

logger = logging.getLogger(__name__)

def api_error_handler(f):
    """Decorator for robust API error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            start_time = time.time()
            result = f(*args, **kwargs)
            
            # Log slow API calls
            duration = time.time() - start_time
            if duration > 2.0:
                logger.warning(f"Slow API call: {request.endpoint} took {duration:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"API Error in {request.endpoint}: {str(e)}")
            logger.error(traceback.format_exc())
            
            return jsonify({
                'error': 'Internal server error',
                'message': 'An error occurred processing your request',
                'endpoint': request.endpoint
            }), 500
            
    return decorated_function

def rate_limit(max_requests=100, window=60):
    """Simple rate limiting decorator"""
    requests = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            now = time.time()
            
            # Clean old requests
            if client_ip in requests:
                requests[client_ip] = [req for req in requests[client_ip] if now - req < window]
            else:
                requests[client_ip] = []
            
            # Check rate limit
            if len(requests[client_ip]) >= max_requests:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {max_requests} requests per {window} seconds'
                }), 429
            
            requests[client_ip].append(now)
            return f(*args, **kwargs)
            
        return decorated_function
    return decorator

# Enhanced API response helper
def api_response(data=None, message=None, status=200):
    """Standardized API response format"""
    response = {
        'success': status < 400,
        'timestamp': time.time(),
        'data': data,
        'message': message
    }
    return jsonify(response), status

# Apply to existing routes
def enhance_existing_routes():
    """Apply enhancements to existing API routes"""
    from routes import app
    
    # Add error handling to all routes
    @app.errorhandler(404)
    def not_found(error):
        return api_response(message='Endpoint not found', status=404)
    
    @app.errorhandler(500)
    def internal_error(error):
        return api_response(message='Internal server error', status=500)
    
    logger.info("API enhancements applied")

if __name__ == "__main__":
    enhance_existing_routes()
