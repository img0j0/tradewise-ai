from app import app

# Import models and routes after app is created
import models
import routes
from api_endpoints_enhanced import enhanced_bp

# Register enhanced features blueprint
app.register_blueprint(enhanced_bp)
