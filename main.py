from app import app
from search_routes import search_bp

# Register blueprints
app.register_blueprint(search_bp)  # noqa: F401
from prometheus_metrics import prometheus_metrics

# Initialize Prometheus metrics
prometheus_metrics.init_app(app)
from routes_enhanced_search import enhanced_search_bp

# Register the enhanced search blueprint (premium_bp already registered in app.py)
app.register_blueprint(enhanced_search_bp)

# Streamlined for competitive focus - enhanced endpoints removed
