from app import app, db

# Import models and routes after app is created
import models
import routes

# Create tables
with app.app_context():
    db.create_all()

# Temporarily disable WebSocket features to fix micro-interactions
# This will resolve the memory issues and worker timeouts

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
