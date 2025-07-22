import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_caching import Cache
from flask_compress import Compress

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.config['SESSION_COOKIE_SECURE'] = False  # Allow cookies over HTTP
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = None  # Allow cross-origin in Replit
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_DOMAIN'] = None  # Let Flask determine the domain
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_for=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///trading_platform.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# initialize the app with the extension
db.init_app(app)

# Initialize WebSocket support
try:
    from websocket_service import init_websocket
    socketio = init_websocket(app)
except ImportError:
    socketio = None

# Initialize caching for better performance
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Initialize compression - temporarily disabled for debugging
# compress = Compress(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'  # type: ignore
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
    
    app.register_blueprint(main_bp)
    app.register_blueprint(premium_bp)
    
    # Global error handlers for professional error pages
    @app.errorhandler(404)
    def page_not_found(error):
        """Custom 404 error page"""
        return render_template('error_404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        """Custom 500 error page"""
        db.session.rollback()
        return render_template('error_500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
