"""
Real-time price updates using WebSocket
"""
from flask_socketio import emit
from stock_search import StockSearchService
import threading
import time
import logging
import json

logger = logging.getLogger(__name__)

# Global socketio instance will be set by setup function
socketio = None

class RealtimeUpdateService:
    def __init__(self):
        self.stock_search = StockSearchService()
        self.active_symbols = set()
        self.update_thread = None
        self.is_running = False
        
    def start_updates(self):
        """Start real-time price updates"""
        if not self.is_running:
            self.is_running = True
            self.update_thread = threading.Thread(target=self._update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()
            logger.info("Real-time updates started")
    
    def stop_updates(self):
        """Stop real-time price updates"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join()
        logger.info("Real-time updates stopped")
    
    def add_symbol(self, symbol):
        """Add symbol to watch list"""
        self.active_symbols.add(symbol.upper())
        logger.info(f"Added {symbol} to real-time updates")
    
    def remove_symbol(self, symbol):
        """Remove symbol from watch list"""
        self.active_symbols.discard(symbol.upper())
        logger.info(f"Removed {symbol} from real-time updates")
    
    def _update_loop(self):
        """Main update loop"""
        while self.is_running:
            try:
                if self.active_symbols:
                    updates = {}
                    for symbol in list(self.active_symbols):
                        try:
                            stock_data = self.stock_search.get_stock_data(symbol)
                            if stock_data:
                                updates[symbol] = {
                                    'symbol': symbol,
                                    'price': stock_data.get('current_price', 0),
                                    'change': stock_data.get('price_change', 0),
                                    'change_percent': stock_data.get('price_change_percent', 0),
                                    'volume': stock_data.get('volume', 0),
                                    'timestamp': time.time()
                                }
                        except Exception as e:
                            logger.error(f"Error updating {symbol}: {e}")
                    
                    if updates:
                        socketio.emit('price_update', {
                            'updates': updates,
                            'timestamp': time.time()
                        }, namespace='/')
                        
                time.sleep(5)  # Update every 5 seconds
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                time.sleep(10)

# Global service instance
realtime_service = RealtimeUpdateService()

def handle_subscribe(data):
    """Handle symbol subscription"""
    symbol = data.get('symbol')
    if symbol:
        realtime_service.add_symbol(symbol)
        emit('subscription_confirmed', {'symbol': symbol})

def handle_unsubscribe(data):
    """Handle symbol unsubscription"""
    symbol = data.get('symbol')
    if symbol:
        realtime_service.remove_symbol(symbol)
        emit('unsubscription_confirmed', {'symbol': symbol})

def handle_connect():
    """Handle client connection"""
    logger.info("Client connected for real-time updates")
    emit('connected', {'status': 'connected'})

def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected from real-time updates")

def setup_realtime_updates(socketio_instance):
    """Setup function to initialize real-time updates with socketio instance"""
    global socketio
    socketio = socketio_instance
    
    # Register event handlers
    socketio.on_event('subscribe_symbol', handle_subscribe)
    socketio.on_event('unsubscribe_symbol', handle_unsubscribe)
    socketio.on_event('connect', handle_connect)
    socketio.on_event('disconnect', handle_disconnect)
    
    # Start the service
    realtime_service.start_updates()
    
    return realtime_service