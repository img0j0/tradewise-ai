from app import app, db

# Import models and routes after app is created
import models
import routes

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Production-ready configuration
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
