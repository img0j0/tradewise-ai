from app import app, db

# Import models and routes after app is created
import models
import routes

# Import WebSocket modules
from websocket_service import init_websocket
from realtime_updates import setup_realtime_updates

# Create tables
with app.app_context():
    db.create_all()

# Initialize WebSocket support
socketio = init_websocket(app)

# Set up real-time update handlers
if socketio:
    realtime_service = setup_realtime_updates(socketio)
    # Make it available to routes
    import routes
    routes.realtime_service = realtime_service

if __name__ == '__main__':
    if socketio:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
