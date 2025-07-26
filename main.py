from app import app
from stock_search_direct import direct_search_bp

# Register direct search blueprint for debugging
app.register_blueprint(direct_search_bp)

# Comment out other blueprints temporarily to avoid conflicts
# from search_routes import search_bp
# from premium_plan_manager import premium_bp
# from routes_premium import premium_routes_bp

# app.register_blueprint(search_bp)
# app.register_blueprint(premium_bp)
# app.register_blueprint(premium_routes_bp)

# Comment out metrics and other blueprints temporarily
# from prometheus_metrics import prometheus_metrics
# prometheus_metrics.init_app(app)
# from routes_enhanced_search import enhanced_search_bp
# app.register_blueprint(enhanced_search_bp)

# Streamlined for competitive focus - enhanced endpoints removed
