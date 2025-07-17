
import asyncio
import json
import logging
from datetime import datetime
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from data_service import DataService
from ai_insights import AIInsightsEngine

logger = logging.getLogger(__name__)

class WebSocketService:
    def __init__(self, app):
        self.socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
        self.data_service = DataService()
        self.ai_engine = AIInsightsEngine()
        self.active_connections = {}
        self.market_data_cache = {}
        
        # Register event handlers
        self.socketio.on_event('connect', self.handle_connect)
        self.socketio.on_event('disconnect', self.handle_disconnect)
        self.socketio.on_event('subscribe_stock', self.handle_subscribe_stock)
        self.socketio.on_event('unsubscribe_stock', self.handle_unsubscribe_stock)
        self.socketio.on_event('get_live_analysis', self.handle_live_analysis)
        
        # Start background tasks
        self.start_market_data_stream()
    
    def handle_connect(self):
        """Handle new WebSocket connection"""
        if current_user.is_authenticated:
            user_id = current_user.id
            self.active_connections[user_id] = {
                'session_id': request.sid,
                'subscribed_stocks': set(),
                'connected_at': datetime.now()
            }
            join_room(f'user_{user_id}')
            logger.info(f"User {user_id} connected via WebSocket")
            
            # Send initial market status
            emit('market_status', {
                'status': 'connected',
                'timestamp': datetime.now().isoformat(),
                'message': 'Real-time market data active'
            })
    
    def handle_disconnect(self):
        """Handle WebSocket disconnection"""
        if current_user.is_authenticated:
            user_id = current_user.id
            if user_id in self.active_connections:
                leave_room(f'user_{user_id}')
                del self.active_connections[user_id]
                logger.info(f"User {user_id} disconnected from WebSocket")
    
    def handle_subscribe_stock(self, data):
        """Handle stock subscription for real-time updates"""
        if current_user.is_authenticated:
            user_id = current_user.id
            symbol = data.get('symbol', '').upper()
            
            if user_id in self.active_connections and symbol:
                self.active_connections[user_id]['subscribed_stocks'].add(symbol)
                join_room(f'stock_{symbol}')
                
                # Send immediate stock data
                stock_data = self.data_service.get_stock_by_symbol(symbol)
                if stock_data:
                    emit('stock_update', {
                        'symbol': symbol,
                        'data': stock_data,
                        'timestamp': datetime.now().isoformat()
                    })
                
                logger.info(f"User {user_id} subscribed to {symbol}")
    
    def handle_unsubscribe_stock(self, data):
        """Handle stock unsubscription"""
        if current_user.is_authenticated:
            user_id = current_user.id
            symbol = data.get('symbol', '').upper()
            
            if user_id in self.active_connections and symbol:
                self.active_connections[user_id]['subscribed_stocks'].discard(symbol)
                leave_room(f'stock_{symbol}')
                logger.info(f"User {user_id} unsubscribed from {symbol}")
    
    def handle_live_analysis(self, data):
        """Handle real-time AI analysis requests"""
        if current_user.is_authenticated:
            symbol = data.get('symbol', '').upper()
            
            if symbol:
                # Get fresh stock data
                stock_data = self.data_service.get_stock_by_symbol(symbol)
                if stock_data:
                    # Generate AI insights
                    insights = self.ai_engine.generate_insights(stock_data)
                    
                    emit('live_analysis', {
                        'symbol': symbol,
                        'insights': insights,
                        'timestamp': datetime.now().isoformat()
                    })
    
    def start_market_data_stream(self):
        """Start background task for streaming market data"""
        def market_data_worker():
            while True:
                try:
                    # Get updated market data
                    market_overview = self.data_service.get_market_overview()
                    
                    # Broadcast to all connected users
                    self.socketio.emit('market_overview_update', {
                        'data': market_overview,
                        'timestamp': datetime.now().isoformat()
                    }, namespace='/')
                    
                    # Update subscribed stocks
                    for user_id, connection in self.active_connections.items():
                        for symbol in connection['subscribed_stocks']:
                            stock_data = self.data_service.get_stock_by_symbol(symbol)
                            if stock_data:
                                self.socketio.emit('stock_update', {
                                    'symbol': symbol,
                                    'data': stock_data,
                                    'timestamp': datetime.now().isoformat()
                                }, room=f'user_{user_id}')
                    
                    asyncio.sleep(5)  # Update every 5 seconds
                    
                except Exception as e:
                    logger.error(f"Error in market data stream: {e}")
                    asyncio.sleep(10)  # Wait longer on error
        
        # Start background thread
        import threading
        market_thread = threading.Thread(target=market_data_worker, daemon=True)
        market_thread.start()

# Global instance
websocket_service = None

def init_websocket(app):
    global websocket_service
    websocket_service = WebSocketService(app)
    return websocket_service.socketio
