import os
import logging
from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_caching import Cache
from flask_compress import Compress

# Production logging configuration
log_level = logging.INFO if os.environ.get('REPLIT_DEPLOYMENT') else logging.DEBUG
logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
# Production security configuration
app.secret_key = os.environ.get("SESSION_SECRET")
if not app.secret_key:
    raise ValueError("SESSION_SECRET environment variable is required for production")

# Production-grade security settings
is_production = bool(os.environ.get('REPLIT_DEPLOYMENT'))
app.config.update({
    'DEBUG': False,  # Always False for production
    'TESTING': False,
    'SECRET_KEY': app.secret_key,
    'SESSION_COOKIE_SECURE': is_production,  # HTTPS only in production
    'SESSION_COOKIE_HTTPONLY': True,  # Prevent XSS attacks
    'SESSION_COOKIE_SAMESITE': 'Strict',  # CSRF protection
    'SESSION_COOKIE_NAME': 'tradewise_session',
    'PERMANENT_SESSION_LIFETIME': 28800,  # 8 hours
    'SESSION_COOKIE_PATH': '/',
    'SESSION_COOKIE_DOMAIN': None,
    'PREFERRED_URL_SCHEME': 'https' if is_production else 'http',
    'WTF_CSRF_ENABLED': True,  # CSRF protection
    'WTF_CSRF_TIME_LIMIT': 3600,  # 1 hour CSRF token lifetime
})

# Enhanced proxy fix for production
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_for=1, x_port=1, x_prefix=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///trading_platform.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# initialize the app with the extension
db.init_app(app)

# Websocket service removed - focusing on competitive features
socketio = None

# Initialize caching for better performance
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutes default
    'CACHE_THRESHOLD': 1000  # Maximum cached items
})

# Initialize performance monitoring
from performance_monitor import monitor
monitor.init_app(app)

# Initialize optimization services after app setup
def initialize_optimization_services():
    """Initialize pre-computation and async task services"""
    try:
        from ai_precomputation_service import precomputation_service
        from async_task_queue import task_queue
        
        # Start background services
        precomputation_service.start_background_service()
        task_queue.start_workers()
        
        print("✅ Optimization services initialized successfully")
        
    except Exception as e:
        print(f"⚠️ Error initializing optimization services: {e}")

# Production security middleware
@app.before_request
def force_https():
    """Force HTTPS in production"""
    if is_production and not request.is_secure and request.url.startswith('http://'):
        return redirect(request.url.replace('http://', 'https://', 1), code=301)

@app.before_request
def security_headers():
    """Add security headers to all responses"""
    pass  # Headers added in after_request

@app.after_request
def add_security_headers(response):
    """Add comprehensive security headers"""
    if is_production:
        response.headers.update({
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://js.stripe.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.stripe.com;",
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        })
    
    # Add performance headers
    response.headers['X-Response-Time'] = getattr(response, '_response_time', '0ms')
    return response

# Start optimization services in background
import threading
threading.Thread(target=initialize_optimization_services, daemon=True).start()

# Initialize compression - temporarily disabled for debugging
# compress = Compress(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'  # type: ignore
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Register blueprints
with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    db.create_all()
    
    # Register blueprints after database setup
    from routes import main_bp
    from premium_routes import premium_bp
    from comprehensive_billing_routes import billing_bp
    from oauth_auth import oauth_bp, create_oauth_blueprints
    from two_factor_auth import twofa_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(premium_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(twofa_bp)
    
    # Register missing API endpoints
    from missing_api_endpoints import missing_api_bp
    app.register_blueprint(missing_api_bp)
    
    # Initialize OAuth blueprints
    try:
        create_oauth_blueprints(app)
        logging.info("OAuth blueprints initialized successfully")
    except Exception as e:
        logging.warning(f"OAuth initialization failed: {e}")
    
    # Initialize billing system
    try:
        from enhanced_stripe_billing import billing_manager
        billing_manager.initialize_plan_configurations()
        logging.info("Billing system initialized successfully")
    except Exception as e:
        logging.warning(f"Billing initialization failed: {e}")
    
    # Add security headers
    from security_headers import add_security_headers
    add_security_headers(app)
    
    # Global error handlers for professional error pages
    @app.errorhandler(404)
    def page_not_found(error):
        """Custom 404 error page"""
        from flask import render_template
        return render_template('error_404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        """Custom 500 error page"""
        from flask import render_template
        db.session.rollback()
        return render_template('error_500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
