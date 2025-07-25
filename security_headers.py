"""
Security Headers Middleware
Adds essential security headers to all responses
"""

from flask import Flask

def add_security_headers(app: Flask):
    """Add security headers to all responses"""
    
    @app.after_request
    def apply_security_headers(response):
        """Apply security headers to every response"""
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (basic)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:;"
        )
        response.headers['Content-Security-Policy'] = csp
        
        return response
    
    return app