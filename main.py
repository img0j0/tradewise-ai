from app import app
from simple_core_routes import simple_core_bp

# Register simple core routes blueprint first
app.register_blueprint(simple_core_bp)

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
