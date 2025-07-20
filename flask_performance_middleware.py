
# Flask Performance Middleware
# Add this to your main Flask application

from flask import Flask, request, make_response, g
import gzip
import io
import time
from functools import wraps

def create_performance_middleware(app):
    """Apply performance optimizations to Flask app"""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        # Add performance headers
        if hasattr(g, 'start_time'):
            response.headers['X-Response-Time'] = str(time.time() - g.start_time)
        
        # Enable compression for text responses
        if (response.content_type.startswith('text/') or 
            response.content_type.startswith('application/json') or
            response.content_type.startswith('application/javascript')):
            
            accept_encoding = request.headers.get('Accept-Encoding', '')
            if 'gzip' in accept_encoding.lower():
                response.direct_passthrough = False
                
                if response.status_code < 200 or response.status_code >= 300:
                    return response
                
                gzip_buffer = io.BytesIO()
                with gzip.GzipFile(fileobj=gzip_buffer, mode='wb') as gzip_file:
                    gzip_file.write(response.get_data())
                
                response.set_data(gzip_buffer.getvalue())
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = len(response.get_data())
        
        # Add caching headers for static assets
        if request.endpoint == 'static':
            response.headers['Cache-Control'] = 'public, max-age=31536000'
            response.headers['Expires'] = 'Thu, 31 Dec 2037 23:55:55 GMT'
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    return app

# Usage: create_performance_middleware(app)
