from app import app, db

# Import models and routes after app is created
import models
import routes

# Create tables
with app.app_context():
    db.create_all()

# WebSocket optimization for App Store deployment
# Disabled WebSocket features to prevent memory issues and worker crashes

if __name__ == '__main__':
    # Production-ready configuration for App Store
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
