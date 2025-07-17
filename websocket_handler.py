
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
import threading
import time
import json
from data_service import DataService
from ai_insights import AIInsightsEngine

socketio = SocketIO()
data_service = DataService()
ai_engine = AIInsightsEngine()

class RealTimeMarketData:
    def __init__(self):
        self.active_connections = {}
        self.is_running = False
        
    def start_market_stream(self):
        """Start real-time market data streaming"""
        if not self.is_running:
            self.is_running = True
            thread = threading.Thread(target=self._market_data_loop)
            thread.daemon = True
            thread.start()
    
    def _market_data_loop(self):
        """Continuously stream market data updates"""
        while self.is_running:
            try:
                # Get latest market data
                stocks = data_service.get_all_stocks()
                market_overview = data_service.get_market_overview()
                
                # Generate AI insights for top movers
                enhanced_data = []
                for stock in stocks[:10]:  # Top 10 stocks
                    insights = ai_engine.generate_insights(stock)
                    stock['real_time_insights'] = insights
                    enhanced_data.append(stock)
                
                # Emit to all connected clients
                socketio.emit('market_update', {
                    'stocks': enhanced_data,
                    'market_overview': market_overview,
                    'timestamp': time.time()
                }, room='market_data')
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"Error in market data loop: {e}")
                time.sleep(5)

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        join_room('market_data')
        emit('status', {'msg': f'User {current_user.username} connected to real-time feed'})

@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room('market_data')

@socketio.on('subscribe_symbol')
def handle_symbol_subscription(data):
    """Subscribe to specific stock symbol updates"""
    symbol = data.get('symbol')
    if symbol and current_user.is_authenticated:
        join_room(f'symbol_{symbol}')
        
        # Send immediate update for this symbol
        stock_data = data_service.get_stock_by_symbol(symbol)
        if stock_data:
            insights = ai_engine.generate_insights(stock_data)
            emit('symbol_update', {
                'symbol': symbol,
                'data': stock_data,
                'insights': insights
            })

# Initialize real-time data handler
real_time_handler = RealTimeMarketData()
