from app import app  # noqa: F401
from routes_enhanced_search import enhanced_search_bp

# Register the enhanced search blueprint (premium_bp already registered in app.py)
app.register_blueprint(enhanced_search_bp)

# Streamlined for competitive focus - enhanced endpoints removed
