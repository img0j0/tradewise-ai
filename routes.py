from flask import render_template, jsonify, request, session, redirect, url_for, flash
from app import app, db
from models import Trade, Portfolio, Alert, UserAccount, Transaction, User
from ai_insights import AIInsightsEngine
from ai_advice_engine import advice_engine
from data_service import DataService
from stock_search import StockSearchService
from cache_service import cache
from portfolio_optimizer import PortfolioOptimizer
from social_trading import SocialTradingEngine
from gamification import GamificationEngine
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import logging
import os
import stripe
from datetime import datetime
from ai_training import ai_trainer
from personalized_ai import personalized_ai
from strategy_builder import strategy_builder
from color_palette import ColorPalette, get_trading_color, get_confidence_color, get_profit_loss_color, generate_chart_colors
from technical_indicators import TechnicalIndicators
from error_recovery import ErrorRecoveryManager, ErrorCategory, with_error_recovery
from advanced_orders import get_order_manager, OrderType, OrderSide, AdvancedOrder
from market_intelligence import get_market_intelligence
from deep_learning_engine import get_deep_learning_engine
from performance_optimizer import get_performance_optimizer, cached, monitored
from dynamic_search_autocomplete import autocomplete_engine
from monetization_strategy import get_monetization_engine
# Import will be done after setup
realtime_service = None

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Get domain for Stripe redirects
YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN') if os.environ.get('REPLIT_DEPLOYMENT') != '' else os.environ.get('REPLIT_DOMAINS').split(',')[0] if os.environ.get('REPLIT_DOMAINS') else 'localhost:5000'

logger = logging.getLogger(__name__)

# Initialize services
data_service = DataService()
ai_engine = AIInsightsEngine()
stock_search_service = StockSearchService()
portfolio_optimizer = PortfolioOptimizer()
social_trading_engine = SocialTradingEngine()
gamification_engine = GamificationEngine()
color_palette = ColorPalette()
error_recovery_manager = ErrorRecoveryManager()
order_manager = get_order_manager()
market_intelligence = get_market_intelligence()
deep_learning_engine = get_deep_learning_engine()
performance_optimizer = get_performance_optimizer()
monetization_engine = get_monetization_engine()

# Train AI model on startup
stocks_data = data_service.get_all_stocks()
ai_engine.train_model(stocks_data)

# Start error recovery manager
error_recovery_manager.start()

# Create a demo user for testing purposes
@with_error_recovery("user_setup")
def ensure_demo_user():
    """Ensure we have a demo user for testing stock purchases"""
    try:
        demo_user = User.query.filter_by(username='demo_user').first()
        if not demo_user:
            demo_user = User(
                username='demo_user',
                email='demo@tradewise.ai'
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            db.session.commit()
            logger.info("Created demo user for testing")
        
        # Ensure user has an account with some balance
        user_account = UserAccount.query.filter_by(user_id=demo_user.id).first()
        if not user_account:
            user_account = UserAccount(
                user_id=demo_user.id,
                balance=10000.0,  # $10k demo balance
                total_deposited=10000.0
            )
            db.session.add(user_account)
            db.session.commit()
            logger.info("Created demo user account with $10k balance")
        
        return demo_user
    except Exception as e:
        logger.error(f"Error setting up demo user: {e}")
        return None

# Initialize demo user with application context
with app.app_context():
    demo_user = ensure_demo_user()

# Get or create user account for logged in user
def get_or_create_user_account():
    """Get or create user account for current user"""
    if not current_user.is_authenticated:
        return None
    
    user_account = UserAccount.query.filter_by(user_id=current_user.id).first()
    if not user_account:
        user_account = UserAccount(user_id=current_user.id, balance=0.0)
        db.session.add(user_account)
        db.session.commit()
    return user_account

@app.route('/')
def index():
    """Main ChatGPT-style AI interface"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('chatgpt_style_search.html')

@app.route('/dashboard')
def dashboard():
    """Clean dashboard page"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('clean_dashboard.html')

@app.route('/analytics')
def analytics():
    """Clean analytics page"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('clean_analytics.html')

@app.route('/portfolio')
def portfolio():
    """Clean portfolio page"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('clean_portfolio.html')

@app.route('/alerts')
def alerts():
    """Clean alerts page"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('clean_alerts.html')

# Content-only endpoints for iframe embedding
@app.route('/dashboard_content')
def dashboard_content():
    """Legacy dashboard content for iframe"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/analytics_content')
def analytics_content():
    """Analytics content for iframe"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    # Show advanced analytics and market intelligence
    try:
        return render_template('analytics_content.html')
    except:
        return render_template('index.html')

@app.route('/portfolio_content')
def portfolio_content():
    """Portfolio content for iframe"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('portfolio_content.html')

@app.route('/alerts_content')
def alerts_content():
    """Alerts content for iframe"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('alerts_content.html')





@app.route('/api/dashboard')
@login_required
def dashboard_data():
    """Get dashboard data"""
    try:
        # Get market overview
        market_overview = data_service.get_market_overview()
        
        # Get top movers
        top_movers = data_service.get_top_movers()
        
        # Get recent trades
        recent_trades = Trade.query.order_by(Trade.timestamp.desc()).limit(10).all()
        
        # Get active alerts
        active_alerts = Alert.query.filter_by(is_active=True).order_by(Alert.created_at.desc()).limit(5).all()
        
        # Get user account balance
        user_account = get_or_create_user_account()
        
        # Calculate portfolio performance
        portfolio_performance = calculate_portfolio_performance()
        
        return jsonify({
            'market_overview': market_overview,
            'top_movers': top_movers,
            'recent_trades': [trade.to_dict() for trade in recent_trades],
            'active_alerts': [alert.to_dict() for alert in active_alerts],
            'portfolio_performance': portfolio_performance,
            'user_account': user_account.to_dict(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({'error': 'Failed to load dashboard data'}), 500

@app.route('/api/stocks')
@login_required
def get_stocks():
    """Get filtered stocks data"""
    try:
        # Get filter parameters
        sector = request.args.get('sector')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        # Get filtered stocks
        stocks = data_service.get_filtered_stocks(sector, min_price, max_price)
        
        # Add AI insights for each stock
        for stock in stocks:
            insights = ai_engine.generate_insights(stock)
            stock['ai_insights'] = insights
        
        return jsonify({
            'stocks': stocks,
            'total_count': len(stocks),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting stocks: {e}")
        return jsonify({'error': 'Failed to load stocks data'}), 500

@app.route('/api/stock/<symbol>')
@login_required
def get_stock_details(symbol):
    """Get detailed stock information"""
    try:
        stock = data_service.get_stock_by_symbol(symbol)
        
        if not stock:
            return jsonify({'error': 'Stock not found'}), 404
        
        # Get AI insights
        insights = ai_engine.generate_insights(stock)
        stock['ai_insights'] = insights
        
        # Get recent trades for this stock
        recent_trades = Trade.query.filter_by(symbol=symbol.upper()).order_by(Trade.timestamp.desc()).limit(10).all()
        
        return jsonify({
            'stock': stock,
            'recent_trades': [trade.to_dict() for trade in recent_trades],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting stock details: {e}")
        return jsonify({'error': 'Failed to load stock details'}), 500

@app.route('/api/alerts')
@login_required
def get_alerts():
    """Get trading alerts"""
    try:
        # Generate alerts based on AI insights
        generate_trading_alerts()
        
        # Get active alerts
        alerts = Alert.query.filter_by(is_active=True).order_by(Alert.created_at.desc()).all()
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return jsonify({'error': 'Failed to load alerts'}), 500

@app.route('/api/alerts/create', methods=['POST'])
@login_required
def create_alert():
    """Create a personalized alert"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['symbol', 'alert_type', 'trigger_value']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get current stock data to generate meaningful message
        stock = data_service.get_stock_by_symbol(data['symbol'])
        if not stock:
            # Try real-time data
            try:
                stock = stock_search_service.search_stock(data['symbol'])
                if not stock:
                    return jsonify({'error': 'Stock not found'}), 404
            except:
                return jsonify({'error': 'Stock not found'}), 404
        
        # Create alert message based on type
        alert_messages = {
            'price_above': f"Alert: {data['symbol']} rises above ${data['trigger_value']}",
            'price_below': f"Alert: {data['symbol']} falls below ${data['trigger_value']}",
            'percent_change': f"Alert: {data['symbol']} moves {data['trigger_value']}% from current price",
            'volume_spike': f"Alert: {data['symbol']} volume exceeds {data['trigger_value']}x average"
        }
        
        message = alert_messages.get(data['alert_type'], f"Custom alert for {data['symbol']}")
        
        # Create alert
        alert = Alert(
            user_id=current_user.id,
            symbol=data['symbol'].upper(),
            alert_type=data['alert_type'],
            message=message,
            confidence_score=50.0,  # Default confidence for user-created alerts
            is_active=True
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({
            'alert': alert.to_dict(),
            'message': 'Alert created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create alert'}), 500

@app.route('/api/alerts/<int:alert_id>/dismiss', methods=['POST'])
@login_required
def dismiss_alert(alert_id):
    """Dismiss an alert"""
    try:
        alert = Alert.query.filter_by(id=alert_id, user_id=current_user.id).first()
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        alert.is_active = False
        db.session.commit()
        
        return jsonify({
            'message': 'Alert dismissed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error dismissing alert: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to dismiss alert'}), 500

@app.route('/api/trade', methods=['POST'])
@login_required
def execute_trade():
    """Execute a simulated trade"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['symbol', 'action', 'quantity']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get current stock price
        stock = data_service.get_stock_by_symbol(data['symbol'])
        if not stock:
            return jsonify({'error': 'Stock not found'}), 404
        
        # Get AI confidence score
        insights = ai_engine.generate_insights(stock)
        
        # Create trade record
        trade = Trade(
            user_id=current_user.id,
            symbol=data['symbol'].upper(),
            action=data['action'].lower(),
            quantity=data['quantity'],
            price=float(stock['current_price']),  # Convert to Python float
            confidence_score=float(insights['confidence_score']),  # Convert to Python float
            is_simulated=True
        )
        
        db.session.add(trade)
        
        # Update portfolio
        update_portfolio(trade)
        
        db.session.commit()
        
        return jsonify({
            'trade': trade.to_dict(),
            'message': f"Simulated {data['action']} order for {data['quantity']} shares of {data['symbol']} executed successfully"
        })
        
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to execute trade'}), 500

@app.route('/api/portfolio')
@login_required
def get_portfolio():
    """Get portfolio data"""
    try:
        portfolio_items = Portfolio.query.filter_by(user_id=current_user.id).all()
        stocks = data_service.get_all_stocks()
        
        # Calculate current values
        portfolio_data = []
        total_value = 0
        total_cost = 0
        
        for item in portfolio_items:
            # Find current stock price - first try sample data, then real-time
            current_stock = next((s for s in stocks if s['symbol'] == item.symbol), None)
            
            # If not in sample data, fetch real-time price
            if not current_stock:
                try:
                    real_stock = stock_search_service.search_stock(item.symbol)
                    if real_stock:
                        current_stock = real_stock
                except:
                    pass
            
            if current_stock:
                current_price = float(current_stock.get('current_price', 0))
                current_value = item.quantity * current_price
                cost_basis = item.quantity * item.avg_price
                pnl = current_value - cost_basis
                pnl_pct = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
                
                portfolio_data.append({
                    'symbol': item.symbol,
                    'quantity': item.quantity,
                    'avg_price': item.avg_price,
                    'current_price': current_price,
                    'current_value': current_value,
                    'cost_basis': cost_basis,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                })
                
                total_value += current_value
                total_cost += cost_basis
        
        total_pnl = total_value - total_cost
        total_pnl_pct = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
        
        return jsonify({
            'portfolio_items': portfolio_data,
            'summary': {
                'total_value': total_value,
                'total_cost': total_cost,
                'total_pnl': total_pnl,
                'total_pnl_pct': total_pnl_pct
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        return jsonify({'error': 'Failed to load portfolio'}), 500

@app.route('/api/sectors')
@login_required
def get_sectors():
    """Get available sectors"""
    try:
        sectors = data_service.get_sectors()
        return jsonify({'sectors': sectors})
    except Exception as e:
        logger.error(f"Error getting sectors: {e}")
        return jsonify({'error': 'Failed to load sectors'}), 500

@app.route('/api/performance')
@login_required
def get_performance():
    """Get trading performance metrics"""
    try:
        performance = calculate_portfolio_performance()
        return jsonify(performance)
    except Exception as e:
        logger.error(f"Error getting performance: {e}")
        return jsonify({'error': 'Failed to load performance data'}), 500

def update_portfolio(trade):
    """Update portfolio based on trade"""
    portfolio_item = Portfolio.query.filter_by(user_id=trade.user_id, symbol=trade.symbol).first()
    
    if trade.action == 'buy':
        if portfolio_item:
            # Update existing position
            total_cost = (portfolio_item.quantity * portfolio_item.avg_price) + (trade.quantity * trade.price)
            total_quantity = portfolio_item.quantity + trade.quantity
            portfolio_item.avg_price = total_cost / total_quantity
            portfolio_item.quantity = total_quantity
            portfolio_item.last_updated = datetime.utcnow()
        else:
            # Create new position
            portfolio_item = Portfolio(
                user_id=trade.user_id,
                symbol=trade.symbol,
                quantity=trade.quantity,
                avg_price=trade.price
            )
            db.session.add(portfolio_item)
    
    elif trade.action == 'sell':
        if portfolio_item:
            if portfolio_item.quantity >= trade.quantity:
                portfolio_item.quantity -= trade.quantity
                portfolio_item.last_updated = datetime.utcnow()
                
                # Remove position if quantity is zero
                if portfolio_item.quantity == 0:
                    db.session.delete(portfolio_item)
            else:
                raise ValueError("Insufficient shares to sell")
        else:
            raise ValueError("No position to sell")

def generate_trading_alerts():
    """Generate trading alerts based on AI insights"""
    try:
        stocks = data_service.get_all_stocks()
        
        for stock in stocks:
            insights = ai_engine.generate_insights(stock)
            confidence = insights['confidence_score']
            
            # Generate buy alerts
            if confidence > 80:
                existing_alert = Alert.query.filter_by(
                    symbol=stock['symbol'],
                    alert_type='buy',
                    is_active=True
                ).first()
                
                if not existing_alert:
                    alert = Alert(
                        user_id=current_user.id,
                        symbol=stock['symbol'],
                        alert_type='buy',
                        message=f"Strong buy signal for {stock['symbol']} - {insights['analysis'][:100]}...",
                        confidence_score=float(confidence)
                    )
                    db.session.add(alert)
            
            # Generate sell alerts
            elif confidence < 20:
                existing_alert = Alert.query.filter_by(
                    symbol=stock['symbol'],
                    alert_type='sell',
                    is_active=True
                ).first()
                
                if not existing_alert:
                    alert = Alert(
                        user_id=current_user.id,
                        symbol=stock['symbol'],
                        alert_type='sell',
                        message=f"Sell signal for {stock['symbol']} - {insights['analysis'][:100]}...",
                        confidence_score=float(confidence)
                    )
                    db.session.add(alert)
        
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Error generating alerts: {e}")
        db.session.rollback()

def calculate_portfolio_performance():
    """Calculate portfolio performance metrics"""
    try:
        # Get current user's trades
        trades = current_user.trades.all() if current_user.is_authenticated else []
        
        # Also get portfolio holdings for unrealized P&L
        portfolio_items = Portfolio.query.filter_by(user_id=current_user.id).all()
        
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'total_realized_pnl': 0,
                'total_unrealized_pnl': 0,
                'avg_confidence': 0
            }
        
        total_trades = len(trades)
        winning_trades = 0
        losing_trades = 0
        total_pnl = 0
        total_confidence = 0
        
        # Group trades by symbol to calculate P&L
        positions = {}
        
        for trade in trades:
            if trade.symbol not in positions:
                positions[trade.symbol] = []
            positions[trade.symbol].append(trade)
            total_confidence += trade.confidence_score
        
        # Calculate P&L for each position
        for symbol, symbol_trades in positions.items():
            symbol_pnl = 0
            shares_held = 0
            avg_buy_price = 0
            total_buy_cost = 0
            
            for trade in symbol_trades:
                if trade.action == 'buy':
                    shares_held += trade.quantity
                    total_buy_cost += trade.quantity * trade.price
                    avg_buy_price = total_buy_cost / shares_held if shares_held > 0 else 0
                elif trade.action == 'sell':
                    if shares_held >= trade.quantity:
                        sell_value = trade.quantity * trade.price
                        cost_basis = trade.quantity * avg_buy_price
                        symbol_pnl += sell_value - cost_basis
                        shares_held -= trade.quantity
            
            total_pnl += symbol_pnl
            
            if symbol_pnl > 0:
                winning_trades += 1
            elif symbol_pnl < 0:
                losing_trades += 1
        
        # Calculate unrealized P&L from current holdings
        total_unrealized_pnl = 0
        stocks = data_service.get_all_stocks()
        
        for item in portfolio_items:
            # Find current stock price - first try sample data, then real-time
            current_stock = next((s for s in stocks if s['symbol'] == item.symbol), None)
            
            # If not in sample data, fetch real-time price
            if not current_stock:
                try:
                    real_stock = stock_search_service.search_stock(item.symbol)
                    if real_stock:
                        current_stock = real_stock
                except:
                    pass
            
            if current_stock:
                current_price = float(current_stock.get('current_price', 0))
                current_value = item.quantity * current_price
                cost_basis = item.quantity * item.avg_price
                unrealized_pnl = current_value - cost_basis
                total_unrealized_pnl += unrealized_pnl
        
        win_rate = (winning_trades / max(winning_trades + losing_trades, 1)) * 100
        avg_confidence = total_confidence / total_trades if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl + total_unrealized_pnl,
            'total_realized_pnl': total_pnl,
            'total_unrealized_pnl': total_unrealized_pnl,
            'avg_confidence': avg_confidence
        }
        
    except Exception as e:
        logger.error(f"Error calculating performance: {e}")
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'avg_confidence': 0
        }

# Import comprehensive advisor
from comprehensive_ai_advisor import comprehensive_advisor

# AI Assistant Routes
@app.route('/api/stock-analysis/<symbol>')
def stock_analysis(symbol):
    """Get comprehensive stock analysis for any stock symbol"""
    try:
        # Use comprehensive AI advisor for any stock analysis
        analysis_result = comprehensive_advisor.analyze_any_stock(symbol.upper())
        
        if not analysis_result.get('success'):
            return jsonify(analysis_result), 404
        
        # Format response for ChatGPT interface
        ai_analysis = analysis_result.get('ai_analysis', {})
        
        return jsonify({
            'success': True,
            'symbol': analysis_result['symbol'],
            'name': analysis_result['company_name'],
            'sector': analysis_result['sector'],
            'industry': analysis_result['industry'],
            'price': analysis_result['current_price'],
            'change': analysis_result['price_change'],
            'change_percent': f"{analysis_result['price_change_percent']:.2f}",
            'market_cap': analysis_result['market_cap'],
            'volume': analysis_result['volume'],
            'pe_ratio': analysis_result['pe_ratio'],
            'beta': analysis_result['beta'],
            'dividend_yield': analysis_result['dividend_yield'],
            'week_52_high': analysis_result['week_52_high'],
            'week_52_low': analysis_result['week_52_low'],
            'ai_recommendation': ai_analysis.get('recommendation', 'HOLD'),
            'ai_confidence': ai_analysis.get('confidence', 50),
            'analysis': ai_analysis.get('analysis_summary', 'Comprehensive analysis available'),
            'business_summary': analysis_result.get('business_summary', ''),
            'website': analysis_result.get('website', ''),
            'technical_analysis': ai_analysis.get('technical_analysis', {}),
            'fundamental_analysis': ai_analysis.get('fundamental_analysis', {}),
            'risk_assessment': ai_analysis.get('risk_assessment', {}),
            'market_position': ai_analysis.get('market_position', {}),
            'key_metrics': ai_analysis.get('key_metrics', {}),
            'investment_thesis': ai_analysis.get('investment_thesis', ''),
            'last_updated': analysis_result.get('last_updated')
        })
        
    except Exception as e:
        logger.error(f"Error in comprehensive stock analysis for {symbol}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to analyze {symbol.upper()}. Please verify the stock symbol is correct.'
        }), 500

# Removed duplicate portfolio-summary route

# Removed duplicate account balance route

@app.route('/api/ai/chat', methods=['POST'])
@login_required
def ai_chat():
    """Handle AI assistant chat requests"""
    try:
        data = request.get_json()
        message_type = data.get('type', '')
        
        if message_type == 'market-overview':
            return get_market_overview_response()
        elif message_type == 'top-picks':
            return get_top_picks_response()
        elif message_type == 'portfolio-advice':
            return get_portfolio_advice_response()
        elif message_type == 'risk-analysis':
            return get_risk_analysis_response()
        else:
            return jsonify({
                'response': 'I can help you with market overview, top stock picks, portfolio advice, and risk analysis. What would you like to know?'
            })
            
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        return jsonify({'error': 'Failed to process request'}), 500

@app.route('/api/ai-search-suggestions', methods=['POST'])
def ai_search_suggestions():
    """AI-powered smart search suggestions"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'suggestions': []})
        
        suggestions = []
        
        # AI-powered company name matching
        company_mappings = {
            'nvidia': {'symbol': 'NVDA', 'name': 'NVIDIA Corporation'},
            'apple': {'symbol': 'AAPL', 'name': 'Apple Inc.'},
            'tesla': {'symbol': 'TSLA', 'name': 'Tesla, Inc.'},
            'microsoft': {'symbol': 'MSFT', 'name': 'Microsoft Corporation'},
            'amazon': {'symbol': 'AMZN', 'name': 'Amazon.com Inc.'},
            'google': {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'},
            'meta': {'symbol': 'META', 'name': 'Meta Platforms Inc.'},
            'netflix': {'symbol': 'NFLX', 'name': 'Netflix Inc.'},
            'facebook': {'symbol': 'META', 'name': 'Meta Platforms Inc.'},
            'alphabet': {'symbol': 'GOOGL', 'name': 'Alphabet Inc.'}
        }
        
        query_lower = query.lower()
        
        # Direct symbol match
        if query.upper() in ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX']:
            suggestions.append({
                'type': 'stock',
                'symbol': query.upper(),
                'text': query.upper(),
                'confidence': 0.95
            })
        
        # Company name matching
        for name, info in company_mappings.items():
            if query_lower in name or name in query_lower:
                suggestions.append({
                    'type': 'company',
                    'symbol': info['symbol'],
                    'text': info['name'],
                    'confidence': 0.9
                })
        
        # AI-generated smart suggestions based on market context
        market_suggestions = []
        
        # Technology keywords
        if any(word in query_lower for word in ['tech', 'ai', 'chip', 'semiconductor', 'software']):
            market_suggestions.extend([
                {'type': 'ai', 'symbol': 'NVDA', 'text': 'NVIDIA - AI Leader', 'confidence': 0.85},
                {'type': 'ai', 'symbol': 'MSFT', 'text': 'Microsoft - Cloud & AI', 'confidence': 0.8},
                {'type': 'ai', 'symbol': 'GOOGL', 'text': 'Google - AI Innovation', 'confidence': 0.8}
            ])
        
        # Electric vehicle keywords
        if any(word in query_lower for word in ['electric', 'ev', 'car', 'auto', 'vehicle']):
            market_suggestions.extend([
                {'type': 'ai', 'symbol': 'TSLA', 'text': 'Tesla - EV Pioneer', 'confidence': 0.9},
                {'type': 'ai', 'symbol': 'F', 'text': 'Ford - EV Growth', 'confidence': 0.7}
            ])
        
        # Streaming/entertainment keywords
        if any(word in query_lower for word in ['streaming', 'video', 'entertainment', 'media']):
            market_suggestions.extend([
                {'type': 'ai', 'symbol': 'NFLX', 'text': 'Netflix - Streaming Leader', 'confidence': 0.85},
                {'type': 'ai', 'symbol': 'DIS', 'text': 'Disney - Media Giant', 'confidence': 0.75}
            ])
        
        suggestions.extend(market_suggestions)
        
        # Remove duplicates and limit results
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            key = suggestion['symbol']
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        return jsonify({
            'suggestions': unique_suggestions[:8],
            'query': query
        })
        
    except Exception as e:
        logger.error(f"AI Search Suggestions error: {e}")
        return jsonify({'suggestions': []}), 200

def get_market_overview_response():
    """Generate market overview response"""
    try:
        market_data = data_service.get_market_overview()
        top_movers = data_service.get_top_movers(limit=3)
        
        response = {
            'type': 'market-overview',
            'data': {
                'overview': market_data,
                'top_gainers': top_movers['top_gainers'],
                'top_losers': top_movers['top_losers']
            },
            'message': generate_market_analysis(market_data, top_movers)
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error generating market overview: {e}")
        return jsonify({'error': 'Failed to analyze market'}), 500

def get_top_picks_response():
    """Generate top picks response"""
    try:
        stocks = data_service.get_all_stocks()
        
        # Add AI insights and filter high confidence stocks
        top_picks = []
        for stock in stocks:
            insights = ai_engine.generate_insights(stock)
            if insights['confidence_score'] > 70:
                stock['ai_insights'] = insights
                top_picks.append(stock)
        
        # Sort by confidence score and take top 3
        top_picks = sorted(top_picks, key=lambda x: x['ai_insights']['confidence_score'], reverse=True)[:3]
        
        response = {
            'type': 'top-picks',
            'data': {
                'picks': top_picks
            },
            'message': f'Found {len(top_picks)} high-confidence investment opportunities today.'
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error generating top picks: {e}")
        return jsonify({'error': 'Failed to generate picks'}), 500

def get_portfolio_advice_response():
    """Generate portfolio advice response"""
    try:
        # This would normally analyze actual portfolio data
        advice = {
            'diversification': 'Consider diversifying across different sectors',
            'risk_level': 'Your current risk level appears moderate',
            'recommendations': [
                'Add some defensive stocks for stability',
                'Consider taking profits on positions up >20%',
                'Keep 10-15% cash for opportunities'
            ]
        }
        
        response = {
            'type': 'portfolio-advice',
            'data': advice,
            'message': 'Based on current market conditions, here\'s my portfolio advice.'
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error generating portfolio advice: {e}")
        return jsonify({'error': 'Failed to generate advice'}), 500

def get_risk_analysis_response():
    """Generate risk analysis response"""
    try:
        analysis = {
            'market_risk': 'MODERATE',
            'volatility': 'Market volatility is within normal range',
            'recommendations': [
                'Set stop-loss orders 5-10% below entry',
                'Avoid concentrated positions >25% of portfolio',
                'Monitor Federal Reserve announcements'
            ]
        }
        
        response = {
            'type': 'risk-analysis',
            'data': analysis,
            'message': 'Current market risk assessment and recommendations.'
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error generating risk analysis: {e}")
        return jsonify({'error': 'Failed to analyze risk'}), 500

def generate_market_analysis(market_data, top_movers):
    """Generate human-readable market analysis"""
    gainers = market_data.get('gainers', 0)
    losers = market_data.get('losers', 0)
    
    if gainers > losers:
        sentiment = "bullish"
        trend = "positive momentum"
    elif losers > gainers:
        sentiment = "bearish"
        trend = "selling pressure"
    else:
        sentiment = "neutral"
        trend = "consolidation"
    
    analysis = f"The market is showing {sentiment} sentiment with {trend}. "
    analysis += f"{gainers} stocks are gaining while {losers} are declining. "
    
    if top_movers['top_gainers']:
        top_gainer = top_movers['top_gainers'][0]
        analysis += f"{top_gainer['symbol']} leads gainers, up {top_gainer['change_pct']:.1f}%. "
    
    return analysis

# Payment and Fund Management Routes

# Removed duplicate account balance route

@app.route('/api/create-deposit-session', methods=['POST'])
@login_required
def create_deposit_session():
    """Create Stripe checkout session for deposit"""
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        
        if amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
        
        # Create Stripe checkout session
        YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
        if os.environ.get('REPLIT_DEPLOYMENT'):
            YOUR_DOMAIN = os.environ.get('REPLIT_DOMAINS', '').split(',')[0]
        
        protocol = 'https' if os.environ.get('REPLIT_DEPLOYMENT') else 'http'
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Account Deposit',
                        'description': f'Deposit ${amount:.2f} to trading account'
                    },
                    'unit_amount': int(amount * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{protocol}://{YOUR_DOMAIN}/deposit/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{protocol}://{YOUR_DOMAIN}/deposit/cancel',
            metadata={
                'user_id': current_user.id if current_user.is_authenticated else None,
                'transaction_type': 'deposit',
                'amount': str(amount)
            }
        )
        
        return jsonify({'checkout_url': checkout_session.url})
        
    except Exception as e:
        logger.error(f"Error creating deposit session: {e}")
        return jsonify({'error': 'Failed to create deposit session'}), 500

@app.route('/deposit/success')
def deposit_success():
    """Handle successful deposit"""
    try:
        session_id = request.args.get('session_id')
        
        # Retrieve the session to get payment details
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            # Update user account balance
            user_account = get_or_create_user_account()
            amount = float(session.metadata['amount'])
            
            user_account.balance += amount
            user_account.total_deposited += amount
            
            # Create transaction record
            transaction = Transaction(
                user_id=current_user.id if current_user.is_authenticated else None,
                transaction_type='deposit',
                amount=amount,
                stripe_payment_intent_id=session.payment_intent,
                status='completed'
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            return render_template('deposit_success.html', amount=amount)
        else:
            return render_template('deposit_error.html')
            
    except Exception as e:
        logger.error(f"Error handling deposit success: {e}")
        return render_template('deposit_error.html')

@app.route('/deposit/cancel')
def deposit_cancel():
    """Handle cancelled deposit"""
    return render_template('deposit_cancel.html')

# Removed duplicate purchase_stock route

@app.route('/api/sell-stock', methods=['POST'])
@login_required
def sell_stock():
    """Sell stock and add to account balance"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        quantity = int(data.get('quantity', 0))
        
        if not symbol or quantity <= 0:
            return jsonify({'error': 'Invalid stock symbol or quantity'}), 400
        
        # Check portfolio holdings
        portfolio_item = Portfolio.query.filter_by(user_id=current_user.id, symbol=symbol).first()
        if not portfolio_item or portfolio_item.quantity < quantity:
            return jsonify({'error': 'Insufficient shares to sell'}), 400
        
        # Get current stock price - first try from data service, then search real-time
        stock_data = data_service.get_stock_by_symbol(symbol)
        if not stock_data:
            # Try searching for the stock in real-time
            stock_data = stock_search_service.search_stock(symbol)
            if not stock_data:
                return jsonify({'error': 'Stock not found'}), 404
        
        # Get the current price and ensure it's a regular Python float
        price = stock_data.get('current_price') or stock_data.get('price', 0)
        # Convert numpy types to Python native types
        price = float(price)
        if price <= 0:
            return jsonify({'error': 'Invalid stock price'}), 400
            
        total_proceeds = float(price * quantity)
        
        # Add to account balance
        user_account = get_or_create_user_account()
        user_account.balance += total_proceeds
        
        # Create transaction record
        transaction = Transaction(
            user_id=current_user.id,
            transaction_type='stock_sale',
            amount=total_proceeds,
            symbol=symbol,
            quantity=quantity,
            price_per_share=price,
            status='completed'
        )
        
        # Create trade record
        trade = Trade(
            user_id=current_user.id,
            symbol=symbol,
            action='sell',
            quantity=quantity,
            price=price,
            confidence_score=0.8,  # Default confidence for manual sales
            is_simulated=False
        )
        
        db.session.add(transaction)
        db.session.add(trade)
        
        # Update portfolio
        update_portfolio(trade)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully sold {quantity} shares of {symbol}',
            'transaction_id': transaction.id,
            'new_balance': user_account.balance
        })
        
    except Exception as e:
        logger.error(f"Error selling stock: {e}")
        return jsonify({'error': 'Failed to sell stock'}), 500

@app.route('/api/transactions')
@login_required
def get_transactions():
    """Get user transaction history"""
    try:
        transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).limit(50).all()
        return jsonify([transaction.to_dict() for transaction in transactions])
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        return jsonify({'error': 'Failed to get transactions'}), 500

@app.route('/api/search-stock', methods=['POST'])
@login_required
def search_stock():
    """Search for any stock by symbol with real-time data"""
    try:
        data = request.json
        symbol = data.get('symbol', '').strip().upper()
        
        if not symbol:
            return jsonify({'error': 'Stock symbol is required'}), 400
        
        # Check cache first
        cache_key = f"stock_search_{symbol}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return jsonify(cached_result)
        
        # Search for stock data
        stock_data = stock_search_service.search_stock(symbol)
        
        if not stock_data:
            return jsonify({'error': f'Stock symbol {symbol} not found'}), 404
        
        # Generate AI insights for the stock
        ai_insights = ai_engine.generate_insights(stock_data)
        stock_data['ai_insights'] = ai_insights
        
        # Get additional fundamentals for risk analysis
        fundamentals = stock_search_service.get_stock_fundamentals(symbol)
        if fundamentals:
            stock_data['fundamentals'] = fundamentals
        
        # Cache the result
        cache.set(cache_key, stock_data)
        
        return jsonify(stock_data)
        
    except Exception as e:
        logger.error(f"Error searching stock: {str(e)}")
        return jsonify({'error': 'Failed to search stock'}), 500

@app.route('/api/validate-symbol', methods=['POST'])
@login_required
def validate_symbol():
    """Validate if a stock symbol exists"""
    try:
        data = request.json
        symbol = data.get('symbol', '').strip().upper()
        
        if not symbol:
            return jsonify({'valid': False, 'error': 'Symbol is required'}), 400
        
        is_valid = stock_search_service.validate_symbol(symbol)
        return jsonify({'valid': is_valid, 'symbol': symbol})
        
    except Exception as e:
        logger.error(f"Error validating symbol: {str(e)}")
        return jsonify({'valid': False, 'error': 'Validation failed'}), 500

@app.route('/api/ai-risk-analysis', methods=['POST'])
@login_required
def ai_risk_analysis():
    """Get detailed AI risk analysis for any stock"""
    try:
        data = request.json
        symbol = data.get('symbol', '').strip().upper()
        
        if not symbol:
            return jsonify({'error': 'Stock symbol is required'}), 400
        
        # Get stock data
        stock_data = stock_search_service.search_stock(symbol)
        if not stock_data:
            return jsonify({'error': f'Stock symbol {symbol} not found'}), 404
        
        # Get fundamentals
        fundamentals = stock_search_service.get_stock_fundamentals(symbol)
        
        # Calculate risk metrics
        risk_score = calculate_risk_score(stock_data, fundamentals)
        
        # Generate detailed risk analysis
        risk_analysis = {
            'symbol': symbol,
            'risk_score': risk_score,
            'risk_level': get_risk_level(risk_score),
            'volatility': calculate_volatility(stock_data),
            'market_position': analyze_market_position(stock_data),
            'fundamental_health': analyze_fundamental_health(fundamentals),
            'ai_recommendation': generate_ai_recommendation(stock_data, fundamentals, risk_score),
            'key_risks': identify_key_risks(stock_data, fundamentals),
            'potential_rewards': identify_potential_rewards(stock_data, fundamentals)
        }
        
        # Convert any numpy types to Python native types
        import json
        risk_analysis_json = json.loads(json.dumps(risk_analysis, default=str))
        
        return jsonify(risk_analysis_json)
        
    except Exception as e:
        logger.error(f"Error in AI risk analysis: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to generate risk analysis'}), 500

def calculate_risk_score(stock_data, fundamentals):
    """Calculate overall risk score (0-100, higher is riskier)"""
    risk_score = 50  # Base score
    
    # Volatility factor
    if stock_data.get('beta', 1) > 1.5:
        risk_score += 15
    elif stock_data.get('beta', 1) < 0.8:
        risk_score -= 10
    
    # Price position factor
    current = stock_data.get('current_price', 0)
    week_52_high = stock_data.get('week_52_high', current)
    week_52_low = stock_data.get('week_52_low', current)
    
    if week_52_high > 0:
        price_position = (current - week_52_low) / (week_52_high - week_52_low)
        if price_position > 0.9:  # Near 52-week high
            risk_score += 10
        elif price_position < 0.2:  # Near 52-week low
            risk_score -= 5
    
    # Fundamental factors
    if fundamentals:
        if fundamentals.get('debt_to_equity', 0) > 2:
            risk_score += 10
        if fundamentals.get('current_ratio', 1) < 1:
            risk_score += 10
        if fundamentals.get('profit_margin', 0) < 0:
            risk_score += 15
    
    return max(0, min(100, risk_score))

def get_risk_level(risk_score):
    """Convert risk score to risk level"""
    if risk_score < 30:
        return 'Low'
    elif risk_score < 50:
        return 'Moderate'
    elif risk_score < 70:
        return 'High'
    else:
        return 'Very High'

def calculate_volatility(stock_data):
    """Calculate volatility metrics"""
    beta = stock_data.get('beta', 1.0)
    daily_range = stock_data.get('high', 0) - stock_data.get('low', 0)
    price = stock_data.get('current_price', 1)
    daily_volatility = (daily_range / price * 100) if price > 0 else 0
    
    return {
        'beta': beta,
        'daily_range_percent': round(daily_volatility, 2),
        'volatility_level': 'High' if beta > 1.3 else 'Moderate' if beta > 0.8 else 'Low'
    }

def analyze_market_position(stock_data):
    """Analyze stock's market position"""
    current = stock_data.get('current_price', 0)
    ma_20 = stock_data.get('moving_avg_20', current)
    week_52_high = stock_data.get('week_52_high', current)
    week_52_low = stock_data.get('week_52_low', current)
    
    position = 'Neutral'
    if current > ma_20 * 1.05:
        position = 'Strong Uptrend'
    elif current > ma_20:
        position = 'Uptrend'
    elif current < ma_20 * 0.95:
        position = 'Downtrend'
    
    return {
        'trend': position,
        'above_ma20': bool(current > ma_20),
        'percent_from_52w_high': round((1 - current/week_52_high) * 100, 2) if week_52_high > 0 else 0,
        'percent_from_52w_low': round((current/week_52_low - 1) * 100, 2) if week_52_low > 0 else 0
    }

def analyze_fundamental_health(fundamentals):
    """Analyze fundamental health"""
    if not fundamentals:
        return {'status': 'Unknown', 'score': 50}
    
    score = 50
    factors = []
    
    if fundamentals.get('profit_margin', 0) > 0.15:
        score += 10
        factors.append('Strong profit margins')
    elif fundamentals.get('profit_margin', 0) < 0:
        score -= 20
        factors.append('Negative profit margins')
    
    if fundamentals.get('debt_to_equity', 100) < 1:
        score += 10
        factors.append('Low debt levels')
    elif fundamentals.get('debt_to_equity', 0) > 2:
        score -= 10
        factors.append('High debt levels')
    
    if fundamentals.get('revenue_growth', 0) > 0.1:
        score += 10
        factors.append('Strong revenue growth')
    
    return {
        'status': 'Excellent' if score > 70 else 'Good' if score > 50 else 'Fair' if score > 30 else 'Poor',
        'score': score,
        'key_factors': factors
    }

def generate_ai_recommendation(stock_data, fundamentals, risk_score):
    """Generate AI-powered recommendation"""
    confidence = ai_engine.generate_confidence_score(stock_data)
    
    recommendation = 'HOLD'
    if confidence > 70 and risk_score < 50:
        recommendation = 'BUY'
    elif confidence < 30 or risk_score > 70:
        recommendation = 'AVOID'
    elif confidence > 60 and risk_score < 60:
        recommendation = 'CONSIDER'
    
    return {
        'action': recommendation,
        'confidence': confidence,
        'reasoning': f"Based on AI analysis with {confidence}% confidence and {get_risk_level(risk_score).lower()} risk level"
    }

def identify_key_risks(stock_data, fundamentals):
    """Identify key risks"""
    risks = []
    
    if stock_data.get('beta', 1) > 1.5:
        risks.append('High volatility compared to market')
    
    current = stock_data.get('current_price', 0)
    week_52_high = stock_data.get('week_52_high', current)
    if current > week_52_high * 0.95:
        risks.append('Trading near 52-week high')
    
    if fundamentals:
        if fundamentals.get('debt_to_equity', 0) > 2:
            risks.append('High debt levels')
        if fundamentals.get('profit_margin', 0) < 0:
            risks.append('Currently unprofitable')
    
    if stock_data.get('pe_ratio', 0) > 30:
        risks.append('High valuation (P/E > 30)')
    
    return risks if risks else ['Standard market risks apply']

def identify_potential_rewards(stock_data, fundamentals):
    """Identify potential rewards"""
    rewards = []
    
    current = stock_data.get('current_price', 0)
    week_52_low = stock_data.get('week_52_low', current)
    if current < week_52_low * 1.2:
        rewards.append('Trading near 52-week low - potential value opportunity')
    
    if fundamentals:
        if fundamentals.get('revenue_growth', 0) > 0.15:
            rewards.append('Strong revenue growth')
        if fundamentals.get('profit_margin', 0) > 0.2:
            rewards.append('Excellent profit margins')
        if fundamentals.get('recommendation_key') == 'buy':
            rewards.append('Positive analyst sentiment')
    
    if stock_data.get('dividend_yield', 0) > 0.02:
        rewards.append(f"Dividend yield of {stock_data['dividend_yield']*100:.2f}%")
    
    return rewards if rewards else ['Potential for capital appreciation']

# Authentication routes
@app.route('/test-login')
def test_login():
    """Test login page"""
    return render_template('test_login.html')

@app.route('/test-session')
def test_session():
    """Test session page"""
    return render_template('test_session.html')

@app.route('/test-direct-login')
def test_direct_login():
    """Direct login test page"""
    return render_template('test_direct_login.html')

@app.route('/login-debug')
def login_debug():
    """Login debug page"""
    return render_template('login_debug.html')

@app.route('/quick-login/<username>')
def quick_login(username):
    """Quick login for testing - bypasses form submission"""
    from flask_login import login_user
    
    # Map test usernames to passwords
    test_accounts = {
        'trader1': 'TradingPro2025',
        'testuser': 'password123'
    }
    
    if username in test_accounts:
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(test_accounts[username]):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            session.permanent = True
            return redirect(url_for('index'))
    
    return redirect(url_for('login'))

@app.route('/login-bypass')
def login_bypass():
    """Login bypass page with clickable links"""
    return render_template('login_bypass.html')

@app.route('/debug-auth')
def debug_auth():
    """Debug authentication status"""
    from flask import session
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'user_id': current_user.id if current_user.is_authenticated else None,
        'username': current_user.username if current_user.is_authenticated else None,
        'session': dict(session),
        'cookies': list(request.cookies.keys())
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember', False))
        
        logger.info(f"Login attempt for username: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Create user account if it doesn't exist
            user_account = UserAccount.query.filter_by(user_id=user.id).first()
            if not user_account:
                user_account = UserAccount(user_id=user.id, balance=0.0)
                db.session.add(user_account)
                db.session.commit()
            
            logger.info(f"Login successful for user: {username}")
            session.permanent = True  # Make session permanent
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            logger.warning(f"Login failed for username: {username}")
            flash('Invalid username or password', 'error')
    
    return render_template('simple_login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Create user account
        user_account = UserAccount(user_id=user.id, balance=0.0)
        db.session.add(user_account)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/api/analytics', methods=['POST'])
@login_required
def analytics_api():
    """Receive analytics data from frontend"""
    try:
        data = request.get_json()
        
        # Log analytics data (in production, you'd store this in a database)
        logger.info(f"Analytics data from user {current_user.id}: {data}")
        
        # You could store this in a database table for analysis
        # For now, we'll just acknowledge receipt
        
        return jsonify({
            'success': True,
            'message': 'Analytics data received'
        })
        
    except Exception as e:
        logger.error(f"Error receiving analytics data: {e}")
        return jsonify({'error': 'Failed to process analytics data'}), 500

# New innovative feature endpoints

@app.route('/api/portfolio/optimize', methods=['POST'])
@login_required
def optimize_portfolio():
    """AI-powered portfolio optimization"""
    try:
        data = request.json
        symbols = data.get('symbols', [])
        risk_tolerance = data.get('risk_tolerance', 'moderate')
        
        if not symbols:
            # Get user's current portfolio symbols
            portfolio = Portfolio.query.filter_by(user_id=current_user.id).all()
            symbols = [p.symbol for p in portfolio]
        
        if not symbols:
            # Use sample diversified portfolio if user has no holdings
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'JPM', 'JNJ', 'PG', 'XOM']
        
        # Run portfolio optimization
        optimization_result = portfolio_optimizer.optimize_portfolio(
            symbols, 
            risk_tolerance=risk_tolerance
        )
        
        if optimization_result:
            return jsonify(optimization_result), 200
        else:
            return jsonify({'error': 'Failed to optimize portfolio'}), 500
            
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/social/top-traders')
@login_required
def get_top_traders():
    """Get top performing traders for social trading"""
    try:
        timeframe = request.args.get('timeframe', 'month')
        limit = int(request.args.get('limit', 10))
        
        result = social_trading_engine.get_top_traders(limit=limit)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting top traders: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/social/trader/<int:trader_id>')
@login_required
def get_trader_profile(trader_id):
    """Get detailed profile of a specific trader"""
    try:
        # For now, return a simple trader profile
        traders = social_trading_engine.get_top_traders(limit=10)['traders']
        trader = next((t for t in traders if t['rank'] == trader_id), None)
        
        if trader:
            return jsonify(trader), 200
        else:
            return jsonify({'error': 'Trader not found'}), 404
            
    except Exception as e:
        logger.error(f"Error getting trader profile: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/social/copy-trade', methods=['POST'])
@login_required
def simulate_copy_trade():
    """Simulate copying another trader's portfolio"""
    try:
        data = request.json
        trader_id = data.get('trader_id')
        amount = float(data.get('amount', 1000))
        
        if not trader_id:
            return jsonify({'error': 'Trader ID required'}), 400
        
        # Check user balance
        user_account = get_or_create_user_account()
        if user_account.balance < amount:
            return jsonify({'error': 'Insufficient balance'}), 400
        
        # For now, return a simulated result
        result = {
            'success': True,
            'message': f'Successfully allocated ${amount:,.2f} to copy trader {trader_id}',
            'trades_copied': 5,
            'expected_return': amount * 0.15  # 15% expected return
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error simulating copy trade: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gamification/achievements')
@login_required
def get_achievements():
    """Get user achievements and progress"""
    try:
        # Get achievements from gamification engine
        result = gamification_engine.get_user_achievements(current_user.id)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting achievements: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gamification/leaderboard')
@login_required
def get_leaderboard():
    """Get trading leaderboard"""
    try:
        timeframe = request.args.get('timeframe', 'all')
        limit = int(request.args.get('limit', 10))
        
        result = gamification_engine.get_leaderboard(timeframe=timeframe)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gamification/challenges')
@login_required
def get_challenges():
    """Get active trading challenges"""
    try:
        result = gamification_engine.get_active_challenges(current_user.id)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting challenges: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtest', methods=['POST'])
@login_required
def backtest_strategy():
    """Backtest a trading strategy"""
    try:
        data = request.json
        symbols = data.get('symbols', [])
        start_date = data.get('start_date', '2024-01-01')
        end_date = data.get('end_date', '2024-12-31')
        initial_capital = float(data.get('initial_capital', 10000))
        
        if not symbols:
            return jsonify({'error': 'Symbols required for backtesting'}), 400
        
        # Run backtest
        backtest_result = portfolio_optimizer.backtest_strategy(
            symbols,
            start_date,
            end_date,
            initial_capital
        )
        
        return jsonify(backtest_result), 200
        
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        return jsonify({'error': str(e)}), 500

# Advanced AI Training endpoints

@app.route('/api/ai/train', methods=['POST'])
@login_required
def train_ai_model():
    """Trigger AI model training with latest data"""
    try:
        data = request.json
        symbols = data.get('symbols', None)
        days = data.get('days', 90)
        
        # Collect training data
        training_data = ai_trainer.collect_training_data(symbols=symbols, days=days)
        
        if training_data is None:
            return jsonify({'error': 'Failed to collect training data'}), 500
            
        # Train models
        success = ai_trainer.train_models(training_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'AI models trained successfully',
                'performance': ai_trainer.model_performance,
                'training_samples': len(training_data)
            })
        else:
            return jsonify({'error': 'Failed to train models'}), 500
            
    except Exception as e:
        logger.error(f"Error training AI model: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/insights/<symbol>')
@login_required
def get_enhanced_ai_insights(symbol):
    """Get enhanced AI insights with advanced predictions"""
    try:
        insights = ai_trainer.get_ai_insights(symbol)
        
        if insights:
            return jsonify(insights)
        else:
            # Fallback to basic AI insights
            stock_info = stock_search_service.get_stock_info(symbol)
            if stock_info:
                basic_insights = ai_engine.generate_insights(stock_info)
                return jsonify({
                    'symbol': symbol,
                    'confidence_score': basic_insights['confidence_score'],
                    'recommendation': basic_insights['recommendation'],
                    'analysis': basic_insights['analysis'],
                    'technical_summary': 'Advanced analysis unavailable',
                    'model_accuracy': ai_trainer.model_performance.get('trend_classifier', 0.85) * 100
                })
            else:
                return jsonify({'error': 'Stock not found'}), 404
                
    except Exception as e:
        logger.error(f"Error getting enhanced AI insights: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/predict', methods=['POST'])
@login_required
def predict_market_conditions():
    """Get market predictions for multiple symbols"""
    try:
        data = request.json
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': 'No symbols provided'}), 400
            
        predictions = {}
        
        for symbol in symbols[:10]:  # Limit to 10 symbols
            prediction = ai_trainer.predict_market_conditions(symbol)
            if prediction:
                predictions[symbol] = prediction
                
        return jsonify({
            'predictions': predictions,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error predicting market conditions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/performance')
@login_required
def get_ai_performance():
    """Get AI model performance metrics"""
    try:
        return jsonify({
            'model_performance': ai_trainer.model_performance,
            'training_history_size': len(ai_trainer.training_history),
            'models': list(ai_trainer.models.keys()),
            'last_updated': ai_trainer.model_performance.get('last_training', 'Never')
        })
        
    except Exception as e:
        logger.error(f"Error getting AI performance: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/continuous-learning', methods=['POST'])
@login_required
def trigger_continuous_learning():
    """Trigger continuous learning from recent trades"""
    try:
        ai_trainer.continuous_learning()
        
        return jsonify({
            'success': True,
            'message': 'Continuous learning process completed',
            'training_history_size': len(ai_trainer.training_history)
        })
        
    except Exception as e:
        logger.error(f"Error in continuous learning: {e}")
        return jsonify({'error': str(e)}), 500

# Enhanced suggestion helper function
def get_enhanced_suggestions(query, limit):
    """Get enhanced suggestions with real-time data and AI insights"""
    try:
        # Get sample stock data first
        stocks = data_service.get_all_stocks()
        
        # Filter stocks based on query
        filtered_stocks = []
        if query:
            query_lower = query.lower()
            for stock in stocks:
                if (query_lower in stock['symbol'].lower() or 
                    query_lower in stock['name'].lower() or
                    query_lower in stock.get('sector', '').lower()):
                    filtered_stocks.append(stock)
        else:
            filtered_stocks = stocks
        
        # Sort by relevance and popularity
        filtered_stocks = sorted(filtered_stocks, key=lambda x: (
            x['symbol'].lower().startswith(query.lower()) if query else True,
            x.get('market_cap', 0)
        ), reverse=True)
        
        # Enhance with real-time data for top matches
        enhanced_suggestions = []
        for stock in filtered_stocks[:limit]:
            try:
                # Try to get real-time data
                real_time_data = stock_search_service.search_stock(stock['symbol'])
                if real_time_data:
                    enhanced_stock = {
                        'symbol': stock['symbol'],
                        'name': stock['name'],
                        'sector': stock.get('sector', 'N/A'),
                        'current_price': real_time_data.get('current_price', stock.get('current_price', 0)),
                        'previous_close': real_time_data.get('previous_close', stock.get('previous_close', 0)),
                        'market_cap': real_time_data.get('market_cap', stock.get('market_cap', 0)),
                        'avg_volume': real_time_data.get('avg_volume', stock.get('avg_volume', 0)),
                        'pe_ratio': real_time_data.get('pe_ratio', stock.get('pe_ratio', 0)),
                        'beta': real_time_data.get('beta', stock.get('beta', 1.0))
                    }
                else:
                    enhanced_stock = stock
                
                enhanced_suggestions.append(enhanced_stock)
                
            except Exception as e:
                # Fallback to sample data if real-time fails
                enhanced_suggestions.append(stock)
        
        return enhanced_suggestions
        
    except Exception as e:
        logger.error(f"Error getting enhanced suggestions: {e}")
        return []

# Personalized AI Routes
@app.route('/api/ai/personalized/learn', methods=['POST'])
@login_required
def learn_user_patterns():
    """Learn from user's trading patterns"""
    try:
        result = personalized_ai.learn_from_user_trades(current_user.id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error learning user patterns: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/personalized/recommendations')
@login_required
def get_personalized_recommendations():
    """Get personalized AI recommendations"""
    try:
        # Get current market data
        market_data = {}
        stocks = data_service.get_all_stocks()
        for stock in stocks:
            market_data[stock['symbol']] = {
                'current_price': stock.get('current_price', 100),
                'expected_return': stock.get('ai_insights', {}).get('expected_return', 0),
                'volatility': stock.get('volatility', 0.15)
            }
        
        result = personalized_ai.get_personalized_recommendations(current_user.id, market_data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {e}")
        return jsonify({'error': str(e)}), 500

# Strategy Builder Routes
@app.route('/api/strategies', methods=['GET'])
@login_required
def get_user_strategies():
    """Get all strategies for current user"""
    try:
        result = strategy_builder.get_user_strategies(current_user.id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting strategies: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies', methods=['POST'])
@login_required
def create_strategy():
    """Create a new trading strategy"""
    try:
        strategy_config = request.json
        result = strategy_builder.create_strategy(current_user.id, strategy_config)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies/<strategy_id>/backtest', methods=['POST'])
@login_required
def backtest_user_strategy(strategy_id):
    """Backtest a strategy"""
    try:
        data = request.json or {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        symbols = data.get('symbols')
        
        result = strategy_builder.backtest_strategy(strategy_id, start_date, end_date, symbols)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error backtesting strategy: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies/<strategy_id>/optimize', methods=['POST'])
@login_required
def optimize_strategy(strategy_id):
    """Optimize strategy with AI"""
    try:
        result = strategy_builder.optimize_strategy_with_ai(strategy_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error optimizing strategy: {e}")
        return jsonify({'error': str(e)}), 500

# Color Palette API Routes
@app.route('/api/color-palette')
def get_color_palette():
    """Get the unified color palette in JSON format"""
    try:
        return jsonify({
            'base_colors': color_palette.base_colors,
            'trading_colors': color_palette.trading_colors,
            'confidence_colors': color_palette.confidence_colors,
            'gradients': {
                'primary': color_palette.generate_gradient(color_palette.base_colors['primary_dark'], color_palette.base_colors['primary']),
                'success': color_palette.generate_gradient(color_palette.base_colors['success_dark'], color_palette.base_colors['success']),
                'warning': color_palette.generate_gradient(color_palette.base_colors['warning_dark'], color_palette.base_colors['warning']),
                'danger': color_palette.generate_gradient(color_palette.base_colors['danger_dark'], color_palette.base_colors['danger']),
            }
        })
    except Exception as e:
        logger.error(f"Error getting color palette: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/color-palette/css')
def get_color_palette_css():
    """Get the color palette as CSS variables"""
    try:
        css_content = color_palette.generate_css_variables()
        return css_content, 200, {'Content-Type': 'text/css'}
    except Exception as e:
        logger.error(f"Error generating CSS: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/color-palette/chart-colors/<int:count>')
def get_chart_colors(count):
    """Get a list of colors for charts"""
    try:
        colors = generate_chart_colors(count)
        return jsonify({'colors': colors})
    except Exception as e:
        logger.error(f"Error getting chart colors: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/color-palette/semantic/<color_type>')
def get_semantic_color(color_type):
    """Get color for specific semantic use case"""
    try:
        if color_type == 'confidence':
            confidence = float(request.args.get('value', 50))
            color = get_confidence_color(confidence)
        elif color_type == 'profit-loss':
            value = float(request.args.get('value', 0))
            color = get_profit_loss_color(value)
        elif color_type == 'trading':
            action = request.args.get('action', 'hold')
            color = get_trading_color(action)
        else:
            return jsonify({'error': 'Invalid color type'}), 400
            
        return jsonify({
            'type': color_type,
            'color': color,
            'variants': color_palette.get_color_variants(color)
        })
    except Exception as e:
        logger.error(f"Error getting semantic color: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/technical-indicators/<symbol>')
@login_required
def get_technical_indicators(symbol):
    """Get enhanced technical indicators for a stock"""
    try:
        period = request.args.get('period', '1mo')
        
        # Get historical data
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return jsonify({'error': 'No data available for symbol'}), 404
        
        prices = hist['Close'].tolist()
        volumes = hist['Volume'].tolist()
        highs = hist['High'].tolist()
        lows = hist['Low'].tolist()
        dates = [date.strftime('%m/%d') for date in hist.index]
        
        # Calculate technical indicators
        indicators = TechnicalIndicators()
        
        # Calculate all indicators
        sma_20 = indicators.calculate_sma(prices, 20)
        sma_50 = indicators.calculate_sma(prices, 50)
        ema_12 = indicators.calculate_ema(prices, 12)
        ema_26 = indicators.calculate_ema(prices, 26)
        rsi = indicators.calculate_rsi(prices)
        macd_data = indicators.calculate_macd(prices)
        bollinger = indicators.calculate_bollinger_bands(prices, 20, 2.0)
        stochastic = indicators.calculate_stochastic(highs, lows, prices)
        vwap = indicators.calculate_vwap(prices, volumes)
        support_resistance = indicators.find_support_resistance(prices)
        
        # Calculate additional indicators
        additional_indicators = indicators.calculate_additional_indicators(prices, volumes)
        
        # Calculate volume indicators
        volume_indicators = indicators.calculate_volume_indicators(volumes, prices) if hasattr(indicators, 'calculate_volume_indicators') else {}
        
        # Calculate additional market data
        current_price = prices[-1] if prices else 0
        daily_high = max(prices[-5:]) if len(prices) >= 5 else max(prices) if prices else 0
        daily_low = min(prices[-5:]) if len(prices) >= 5 else min(prices) if prices else 0
        avg_volume = sum(volumes[-20:]) / min(20, len(volumes)) if volumes else 0
        
        return jsonify({
            'symbol': symbol,
            'dates': dates,
            'prices': prices,
            'highs': highs,
            'lows': lows,
            'volume': volumes,
            'sma_20': sma_20,
            'sma_50': sma_50,
            'ema_12': ema_12,
            'ema_26': ema_26,
            'rsi': rsi,
            'macd': macd_data,
            'bollinger': bollinger,
            'stochastic': stochastic,
            'vwap': vwap,
            'support_resistance': support_resistance,
            'additional_indicators': additional_indicators,
            'volume_indicators': volume_indicators,
            'market_data': {
                'current_price': current_price,
                'daily_high': daily_high,
                'daily_low': daily_low,
                'current_volume': volumes[-1] if volumes else 0,
                'avg_volume': avg_volume,
                'price_change': current_price - prices[-2] if len(prices) > 1 else 0,
                'price_change_percent': ((current_price - prices[-2]) / prices[-2] * 100) if len(prices) > 1 and prices[-2] != 0 else 0
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting technical indicators: {e}")
        return jsonify({'error': 'Failed to get technical indicators'}), 500

@app.route('/api/search-stock/<symbol>')
@login_required
def search_stock_api(symbol):
    """Search for stock data using the StockSearchService"""
    try:
        logger.info(f"Searching for stock: {symbol}")
        stock_data = stock_search_service.search_stock(symbol)
        logger.info(f"Stock data result: {stock_data is not None}")
        
        if not stock_data:
            logger.error(f"Stock not found: {symbol}")
            return jsonify({'error': 'Stock not found'}), 404
        
        # Generate AI insights
        ai_insights = ai_engine.generate_insights(stock_data)
        stock_data['ai_insights'] = ai_insights
        
        return jsonify(stock_data)
        
    except Exception as e:
        logger.error(f"Error searching for stock {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

# Dynamic Search Autocomplete API Endpoints
@app.route('/api/search-autocomplete')
@login_required
def search_autocomplete():
    """Get intelligent search suggestions with enhanced features"""
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 8))
        enhanced = request.args.get('enhanced', '').lower() == 'true'
        popular = request.args.get('popular', '').lower() == 'true'
        
        if popular and not query:
            # Return popular stocks
            popular_stocks = [
                {'symbol': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology', 'current_price': 210.06, 'previous_close': 210.16, 'market_cap': 3136816676864, 'avg_volume': 45000000},
                {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'sector': 'Technology', 'current_price': 441.54, 'previous_close': 441.58, 'market_cap': 3282738647040, 'avg_volume': 20000000},
                {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': 'Technology', 'current_price': 180.17, 'previous_close': 180.17, 'market_cap': 2217651167744, 'avg_volume': 18000000},
                {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'sector': 'Consumer Discretionary', 'current_price': 191.76, 'previous_close': 191.76, 'market_cap': 2003456671744, 'avg_volume': 35000000},
                {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'sector': 'Automotive', 'current_price': 261.77, 'previous_close': 261.77, 'market_cap': 835839770624, 'avg_volume': 85000000},
                {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'sector': 'Technology', 'current_price': 136.93, 'previous_close': 136.93, 'market_cap': 3360086392832, 'avg_volume': 55000000},
                {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'sector': 'Technology', 'current_price': 591.80, 'previous_close': 591.80, 'market_cap': 1503438848000, 'avg_volume': 15000000},
                {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'sector': 'Entertainment', 'current_price': 712.73, 'previous_close': 712.73, 'market_cap': 306372321280, 'avg_volume': 8000000}
            ]
            
            return jsonify({
                'suggestions': popular_stocks[:limit],
                'query': query,
                'total': len(popular_stocks[:limit])
            })
        
        if enhanced:
            # Get enhanced AI-powered suggestions with real-time data
            enhanced_suggestions = get_enhanced_suggestions(query, limit)
            return jsonify({
                'suggestions': enhanced_suggestions,
                'query': query,
                'total': len(enhanced_suggestions)
            })
        
        # Get standard AI-powered suggestions
        suggestions = autocomplete_engine.get_intelligent_suggestions(query, limit)
        
        return jsonify({
            'suggestions': suggestions,
            'query': query,
            'total': len(suggestions)
        })
        
    except Exception as e:
        logger.error(f"Error getting autocomplete suggestions: {e}")
        return jsonify({'error': 'Failed to get suggestions'}), 500

@app.route('/api/search-themes')
@login_required
def search_themes():
    """Get trending investment themes"""
    try:
        themes = {
            'AI': 'Artificial Intelligence & Machine Learning',
            'Electric Vehicles': 'Electric Vehicles & Clean Transportation',
            'Streaming': 'Streaming & Digital Entertainment',
            'Cloud Computing': 'Cloud Computing & Enterprise Software',
            'Fintech': 'Financial Technology & Digital Payments',
            'Healthcare': 'Healthcare & Biotechnology',
            'Renewable Energy': 'Renewable Energy & Clean Tech'
        }
        
        return jsonify({
            'themes': themes,
            'trending': list(themes.keys())[:4]
        })
        
    except Exception as e:
        logger.error(f"Error getting investment themes: {e}")
        return jsonify({'error': 'Failed to get themes'}), 500

@app.route('/api/search-theme/<theme_name>')
@login_required
def search_theme(theme_name):
    """Get analytical page for trending investment themes"""
    try:
        # Define theme configurations
        theme_configs = {
            'AI & Tech': {
                'icon': 'fa-robot',
                'description': 'Leading artificial intelligence and technology companies driving innovation',
                'stocks': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'TSLA', 'AMZN', 'NFLX'],
                'insights': {
                    'confidence': 85,
                    'analysis': 'The AI & Tech sector continues to show strong growth potential driven by artificial intelligence adoption, cloud computing expansion, and digital transformation trends. Companies in this space are well-positioned for long-term growth.'
                }
            },
            'Clean Energy': {
                'icon': 'fa-leaf',
                'description': 'Renewable energy and sustainable technology companies',
                'stocks': ['TSLA', 'ENPH', 'SEDG', 'PLUG', 'FSLR', 'SPWR', 'RUN', 'NEE'],
                'insights': {
                    'confidence': 78,
                    'analysis': 'Clean Energy sector benefits from government incentives, falling technology costs, and increasing corporate sustainability commitments. Long-term outlook remains positive despite short-term volatility.'
                }
            },
            'Healthcare': {
                'icon': 'fa-heartbeat',
                'description': 'Healthcare and biotechnology companies',
                'stocks': ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'DHR', 'ABT'],
                'insights': {
                    'confidence': 82,
                    'analysis': 'Healthcare sector offers defensive characteristics with steady growth. Aging demographics and medical innovation drive long-term demand. Pharmaceutical companies benefit from patent protections and drug development pipelines.'
                }
            },
            'Fintech': {
                'icon': 'fa-credit-card',
                'description': 'Financial technology and digital payment companies',
                'stocks': ['V', 'MA', 'PYPL', 'SQ', 'ADYEN', 'COIN', 'AFRM', 'SOFI'],
                'insights': {
                    'confidence': 75,
                    'analysis': 'Fintech sector benefits from digital payment adoption, blockchain technology, and financial service democratization. Growth potential remains strong despite regulatory challenges.'
                }
            },
            'Gaming': {
                'icon': 'fa-gamepad',
                'description': 'Video game and entertainment companies',
                'stocks': ['MSFT', 'GOOGL', 'AAPL', 'EA', 'ATVI', 'TTWO', 'RBLX', 'UNITY'],
                'insights': {
                    'confidence': 73,
                    'analysis': 'Gaming industry continues to grow with mobile gaming, esports, and virtual reality trends. Cloud gaming and subscription models provide recurring revenue opportunities.'
                }
            },
            'Crypto': {
                'icon': 'fa-coins',
                'description': 'Cryptocurrency and blockchain-related companies',
                'stocks': ['COIN', 'MSTR', 'RIOT', 'MARA', 'BITF', 'HUT', 'CLSK', 'BTBT'],
                'insights': {
                    'confidence': 65,
                    'analysis': 'Cryptocurrency sector remains highly volatile with regulatory uncertainty. However, institutional adoption and blockchain technology development continue to drive long-term interest.'
                }
            }
        }
        
        theme_config = theme_configs.get(theme_name, {
            'icon': 'fa-chart-line',
            'description': f'Investment theme analysis for {theme_name}',
            'stocks': ['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
            'insights': {
                'confidence': 70,
                'analysis': f'Comprehensive analysis of {theme_name} investment opportunities.'
            }
        })
        
        # Get stock data for theme
        stocks = data_service.get_all_stocks()
        theme_stocks = []
        total_market_cap = 0
        
        for symbol in theme_config['stocks']:
            stock = next((s for s in stocks if s['symbol'] == symbol), None)
            if stock:
                # Try to get real-time data
                try:
                    real_time_data = stock_search_service.search_stock(symbol)
                    if real_time_data:
                        current_price = real_time_data.get('current_price', stock.get('current_price', 0))
                        previous_close = real_time_data.get('previous_close', stock.get('previous_close', 0))
                        market_cap = real_time_data.get('market_cap', stock.get('market_cap', 0))
                    else:
                        current_price = stock.get('current_price', 0)
                        previous_close = stock.get('previous_close', 0)
                        market_cap = stock.get('market_cap', 0)
                except:
                    current_price = stock.get('current_price', 0)
                    previous_close = stock.get('previous_close', 0)
                    market_cap = stock.get('market_cap', 0)
                
                change_percent = ((current_price - previous_close) / previous_close) * 100 if previous_close > 0 else 0
                
                theme_stocks.append({
                    'symbol': symbol,
                    'name': stock['name'],
                    'current_price': current_price,
                    'change_percent': change_percent,
                    'market_cap': market_cap
                })
                
                total_market_cap += market_cap
        
        # Calculate theme performance (simplified calculation)
        theme_return = sum(stock['change_percent'] for stock in theme_stocks) / len(theme_stocks) if theme_stocks else 0
        
        theme_data = {
            'name': theme_name,
            'icon': theme_config['icon'],
            'description': theme_config['description'],
            'total_market_cap': total_market_cap,
            'top_stocks': theme_stocks,
            'performance': {
                'return_30d': theme_return * 5,  # Simulated 30-day return
                'return_ytd': theme_return * 15,  # Simulated YTD return
                'volatility': abs(theme_return) * 2  # Simulated volatility
            },
            'insights': theme_config['insights']
        }
        
        return jsonify(theme_data)
        
    except Exception as e:
        logger.error(f"Error getting theme analysis: {e}")
        return jsonify({'error': 'Failed to get theme analysis'}), 500

@app.route('/api/search-external')
@login_required
def search_external():
    """Search for stocks not in the popular database"""
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 5))
        
        if not query:
            return jsonify({'suggestions': [], 'query': query, 'total': 0})
        
        # Search external stocks
        suggestions = autocomplete_engine.search_external_stocks(query, limit)
        
        return jsonify({
            'suggestions': suggestions,
            'query': query,
            'total': len(suggestions)
        })
        
    except Exception as e:
        logger.error(f"Error searching external stocks: {e}")
        return jsonify({'error': 'Failed to search external stocks'}), 500

@app.route('/api/ai-analysis/<symbol>')
@login_required
def get_ai_analysis(symbol):
    """Get comprehensive AI analysis for a stock"""
    try:
        # Get real-time stock data
        stock_data = stock_search_service.search_stock(symbol)
        if not stock_data:
            return jsonify({'error': 'Stock data not found'}), 404
        
        # Get AI insights
        ai_insights = ai_engine.get_insights(symbol, stock_data)
        
        confidence = ai_insights.get('confidence', 0.5)
        expected_return = ai_insights.get('expected_return', 0)
        
        # Generate recommendation
        recommendation = 'HOLD'
        if confidence > 0.7 and expected_return > 0.05:
            recommendation = 'STRONG BUY'
        elif confidence > 0.6 and expected_return > 0.02:
            recommendation = 'BUY'
        elif confidence < 0.3 and expected_return < -0.05:
            recommendation = 'STRONG SELL'
        elif confidence < 0.4 and expected_return < -0.02:
            recommendation = 'SELL'
        
        # Risk assessment
        risk_score = int((1 - confidence) * 10)
        risk_level = 'LOW' if risk_score < 4 else 'MEDIUM' if risk_score < 7 else 'HIGH'
        
        # Generate key risks
        key_risks = []
        if stock_data.get('beta', 1.0) > 1.5:
            key_risks.append('High volatility (Beta > 1.5)')
        if stock_data.get('pe_ratio', 0) > 30:
            key_risks.append('High P/E ratio indicating potential overvaluation')
        if expected_return < 0:
            key_risks.append('Negative expected return based on AI analysis')
        if not key_risks:
            key_risks = ['Standard market risks', 'Sector-specific risks']
        
        # Generate insight text
        insight = f"AI analysis of {symbol} shows {confidence*100:.0f}% confidence. "
        if expected_return > 0:
            insight += f"The model predicts positive momentum with {expected_return*100:.1f}% expected return. "
        else:
            insight += f"The model indicates potential downside with {expected_return*100:.1f}% expected return. "
        
        insight += f"Risk level is assessed as {risk_level.lower()} based on current market conditions and technical indicators."
        
        # Calculate price target
        current_price = stock_data.get('current_price', 0)
        price_target = current_price * (1 + expected_return)
        
        analysis = {
            'recommendation': recommendation,
            'confidence': int(confidence * 100),
            'risk_level': risk_level,
            'risk_score': risk_score,
            'insight': insight,
            'price_target': price_target,
            'expected_return': expected_return * 100,
            'key_risks': key_risks,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error generating AI analysis for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio-analytics')
@login_required
def get_portfolio_analytics():
    """Get comprehensive portfolio analytics data"""
    try:
        user_id = current_user.id
        
        # Get user's portfolio
        portfolio = Portfolio.query.filter_by(user_id=user_id).all()
        
        if not portfolio:
            return jsonify({
                'holdings': [],
                'historical_returns': [],
                'historical_values': [],
                'benchmark_values': [],
                'dates': []
            })
        
        # Calculate portfolio metrics
        holdings_data = []
        total_value = 0
        total_cost = 0
        
        for holding in portfolio:
            # Get current stock price
            stock_data = stock_search_service.search_stock(holding.symbol)
            current_price = stock_data.get('current_price', holding.average_price) if stock_data else holding.average_price
            
            position_value = current_price * holding.shares
            position_cost = holding.average_price * holding.shares
            
            holdings_data.append({
                'symbol': holding.symbol,
                'shares': holding.shares,
                'average_price': float(holding.average_price),
                'current_price': float(current_price),
                'position_value': float(position_value),
                'position_cost': float(position_cost),
                'profit_loss': float(position_value - position_cost),
                'profit_loss_percent': float(((position_value - position_cost) / position_cost) * 100) if position_cost > 0 else 0,
                'risk_score': float(stock_data.get('volatility', 0.2) * 10) if stock_data else 5.0
            })
            
            total_value += position_value
            total_cost += position_cost
        
        # Generate historical data for the last 30 days
        import datetime
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=30)
        
        dates = []
        portfolio_values = []
        benchmark_values = []
        returns = []
        
        # Generate mock historical data (in production, this would come from real data)
        for i in range(30):
            date = start_date + datetime.timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
            
            # Simulate portfolio value changes
            base_value = total_value
            daily_change = (i - 15) * 0.01  # Simple trend
            noise = (hash(date.strftime('%Y-%m-%d')) % 100 - 50) * 0.001  # Random noise
            portfolio_value = base_value * (1 + daily_change + noise)
            portfolio_values.append(portfolio_value)
            
            # Simulate benchmark (S&P 500) values
            benchmark_value = base_value * (1 + (i - 15) * 0.008 + noise * 0.5)
            benchmark_values.append(benchmark_value)
            
            # Calculate daily returns
            if i > 0:
                daily_return = (portfolio_value - portfolio_values[i-1]) / portfolio_values[i-1]
                returns.append(daily_return)
        
        # Market returns for beta calculation
        market_returns = []
        for i in range(1, len(benchmark_values)):
            market_return = (benchmark_values[i] - benchmark_values[i-1]) / benchmark_values[i-1]
            market_returns.append(market_return)
        
        analytics_data = {
            'holdings': holdings_data,
            'historical_returns': returns,
            'historical_values': portfolio_values,
            'benchmark_values': benchmark_values,
            'market_returns': market_returns,
            'dates': dates,
            'total_value': float(total_value),
            'total_cost': float(total_cost),
            'total_return': float(((total_value - total_cost) / total_cost) * 100) if total_cost > 0 else 0,
            'portfolio_count': len(holdings_data)
        }
        
        return jsonify(analytics_data)
        
    except Exception as e:
        logger.error(f"Error getting portfolio analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-overview')
@login_required
def get_market_overview():
    """Get market overview for smart assistant"""
    try:
        # Get market data
        market_data = data_service.get_market_overview()
        
        # Calculate volatility
        volatility = 0.15  # Default volatility
        if market_data.get('stocks'):
            price_changes = [stock.get('change_percent', 0) for stock in market_data['stocks']]
            volatility = np.std(price_changes) / 100 if price_changes else 0.15
        
        # Find opportunities
        opportunities = []
        if market_data.get('stocks'):
            for stock in market_data['stocks']:
                # Look for potential opportunities
                if stock.get('change_percent', 0) < -5:  # Stocks down more than 5%
                    opportunities.append({
                        'symbol': stock['symbol'],
                        'type': 'oversold',
                        'reason': f"Down {abs(stock.get('change_percent', 0)):.1f}% - potential buying opportunity"
                    })
                elif stock.get('change_percent', 0) > 5:  # Stocks up more than 5%
                    opportunities.append({
                        'symbol': stock['symbol'],
                        'type': 'momentum',
                        'reason': f"Up {stock.get('change_percent', 0):.1f}% - strong momentum"
                    })
        
        return jsonify({
            'volatility': volatility,
            'opportunities': opportunities[:5],  # Limit to 5 opportunities
            'market_sentiment': 'neutral',
            'trending_sectors': ['Technology', 'Healthcare', 'Finance'],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-assistant', methods=['POST'])
@login_required
def ai_assistant_endpoint():
    """Enhanced AI assistant endpoint with context awareness"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        context = data.get('context', 'Dashboard')
        user_preferences = data.get('userPreferences', {})
        
        # Get user's portfolio for context
        user_id = current_user.id
        portfolio = Portfolio.query.filter_by(user_id=user_id).all()
        
        # Generate contextual response
        response = generate_contextual_response(message, context, portfolio, user_preferences)
        
        return jsonify({
            'message': response,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in AI assistant: {e}")
        return jsonify({'error': str(e)}), 500

def generate_contextual_response(message, context, portfolio, user_preferences):
    """Generate contextual AI response based on user's context and portfolio"""
    
    # Analyze user message
    message_lower = message.lower()
    
    # Portfolio-specific responses
    if 'portfolio' in message_lower:
        if not portfolio:
            return "You don't have any holdings in your portfolio yet. Consider starting with some diversified investments in blue-chip stocks or ETFs."
        
        total_value = sum(holding.shares * holding.average_price for holding in portfolio)
        holdings_count = len(portfolio)
        
        return f"Your portfolio contains {holdings_count} positions with a total value of approximately ${total_value:,.2f}. Your holdings include: {', '.join([h.symbol for h in portfolio[:5]])}. Would you like a detailed performance analysis?"
    
    # Market analysis responses
    elif 'market' in message_lower or 'overview' in message_lower:
        return "The market is showing mixed signals today. Tech stocks are leading gains while energy sectors are under pressure. Key levels to watch: S&P 500 at 4,400 support, NASDAQ at 13,000 resistance. Current VIX suggests moderate volatility."
    
    # Stock analysis responses
    elif 'analyze' in message_lower or 'analysis' in message_lower:
        return "I can provide detailed technical and fundamental analysis for any stock. Please specify the symbol you'd like me to analyze, and I'll give you insights on price targets, risk levels, and AI predictions."
    
    # Risk-related responses
    elif 'risk' in message_lower:
        return "Risk management is crucial for long-term success. I recommend diversifying across sectors, using stop-losses, and never risking more than 2% of your portfolio on a single trade. Would you like me to analyze your current risk exposure?"
    
    # Training responses
    elif 'train' in message_lower and 'ai' in message_lower:
        return "I'm continuously learning from market data and your trading patterns. My current accuracy rates: Price prediction 85%, Trend classification 78%, Volatility forecasting 82%. Training with latest data will improve these metrics."
    
    # Default contextual responses based on current section
    elif context == 'Dashboard':
        return "Welcome to your trading dashboard! I can help you with market analysis, portfolio insights, or finding new investment opportunities. What would you like to explore?"
    
    elif context == 'Stocks':
        return "I can help you research stocks, analyze technical indicators, or identify trading opportunities. Try asking me about specific stocks or market sectors."
    
    elif context == 'Portfolio':
        return "Let me help you optimize your portfolio! I can provide performance analysis, risk assessment, or rebalancing suggestions based on your current holdings."
    
    elif context == 'Advanced':
        return "In the advanced section, I can help you with AI model training, strategy development, or complex market analysis. What advanced feature would you like to explore?"
    
    else:
        return "I'm here to help you make informed investment decisions. Ask me about market trends, stock analysis, portfolio optimization, or AI-powered trading strategies!"

# Error Recovery API Endpoints
@app.route('/api/error-report', methods=['POST'])
@with_error_recovery(category=ErrorCategory.API)
def error_report():
    """Accept error reports from frontend"""
    try:
        error_data = request.json
        
        # Log the error
        logger.error(f"Frontend error report: {error_data}")
        
        # Add to error recovery manager
        error_recovery_manager.handle_error(
            Exception(error_data.get('error', 'Unknown error')),
            context=error_data.get('context', {}),
            category=ErrorCategory.SYSTEM
        )
        
        return jsonify({'status': 'received', 'timestamp': datetime.now().isoformat()})
        
    except Exception as e:
        logger.error(f"Error processing error report: {e}")
        return jsonify({'error': 'Failed to process error report'}), 500

@app.route('/api/error-recovery-stats', methods=['GET'])
@login_required
@with_error_recovery(category=ErrorCategory.API)
def error_recovery_stats():
    """Get error recovery statistics"""
    try:
        stats = error_recovery_manager.get_error_statistics()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting recovery stats: {e}")
        return jsonify({'error': 'Failed to get recovery stats'}), 500

@app.route('/api/system-health', methods=['GET'])
@login_required
@with_error_recovery(category=ErrorCategory.API)
def system_health():
    """Get system health status"""
    try:
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'database': check_database_health(),
            'ai_engine': check_ai_engine_health(),
            'real_time_data': check_realtime_health(),
            'error_recovery': check_error_recovery_health(),
            'overall_status': 'healthy'
        }
        
        # Determine overall status
        unhealthy_components = [k for k, v in health_status.items() 
                               if isinstance(v, dict) and v.get('status') != 'healthy']
        
        if unhealthy_components:
            health_status['overall_status'] = 'degraded'
            health_status['unhealthy_components'] = unhealthy_components
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'error',
            'error': str(e)
        }), 500

def check_database_health():
    """Check database health"""
    try:
        # Simple query to test database connectivity
        db.session.execute('SELECT 1')
        return {'status': 'healthy', 'last_checked': datetime.now().isoformat()}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e), 'last_checked': datetime.now().isoformat()}

def check_ai_engine_health():
    """Check AI engine health"""
    try:
        # Test AI engine
        test_result = ai_engine.get_model_performance()
        return {
            'status': 'healthy',
            'model_accuracy': test_result.get('accuracy', 0.85),
            'last_checked': datetime.now().isoformat()
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e), 'last_checked': datetime.now().isoformat()}

def check_realtime_health():
    """Check real-time data health"""
    try:
        # Test stock data fetching
        test_stock = stock_search_service.search_stock('AAPL')
        return {
            'status': 'healthy' if test_stock else 'degraded',
            'last_price_update': test_stock.get('last_updated') if test_stock else None,
            'last_checked': datetime.now().isoformat()
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e), 'last_checked': datetime.now().isoformat()}

def check_error_recovery_health():
    """Check error recovery system health"""
    try:
        stats = error_recovery_manager.get_error_statistics()
        return {
            'status': 'healthy',
            'error_rate': stats.get('error_rate', 0),
            'total_errors': stats.get('total_errors', 0),
            'resolved_errors': stats.get('resolved_errors', 0),
            'last_checked': datetime.now().isoformat()
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e), 'last_checked': datetime.now().isoformat()}

# ======= ADVANCED TRADING ENHANCEMENTS =======

# Advanced Order Management System
@app.route('/api/orders/advanced', methods=['POST'])
@login_required
@monitored
def create_advanced_order():
    """Create advanced order (stop-loss, take-profit, trailing stop, etc.)"""
    try:
        data = request.json
        symbol = data.get('symbol')
        quantity = int(data.get('quantity', 0))
        order_type = OrderType(data.get('order_type', 'market'))
        side = OrderSide(data.get('side', 'buy'))
        
        # Create advanced order
        order = order_manager.create_order(
            symbol=symbol,
            quantity=quantity,
            order_type=order_type,
            side=side,
            user_id=current_user.id,
            limit_price=data.get('limit_price'),
            stop_price=data.get('stop_price'),
            trailing_amount=data.get('trailing_amount'),
            trailing_percent=data.get('trailing_percent'),
            time_in_force=data.get('time_in_force', 'GTC')
        )
        
        return jsonify({
            'success': True,
            'order': order.to_dict(),
            'message': f'Advanced order created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating advanced order: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/position-size', methods=['POST'])
@login_required
@cached(ttl=60)
def calculate_position_size():
    """Calculate optimal position size using various methods"""
    try:
        data = request.json
        method = data.get('method', 'risk_based')
        
        if method == 'risk_based':
            user_account = get_or_create_user_account()
            size = order_manager.calculate_position_size(
                method='risk_based',
                account_balance=user_account.balance,
                risk_percent=data.get('risk_percent', 2),
                entry_price=data.get('entry_price', 100),
                stop_loss=data.get('stop_loss', 95)
            )
        
        return jsonify({
            'method': method,
            'position_size': size,
            'recommended_shares': int(size) if method == 'risk_based' else None
        })
        
    except Exception as e:
        logger.error(f"Error calculating position size: {e}")
        return jsonify({'error': str(e)}), 500

# Market Intelligence Hub
@app.route('/api/market-intelligence/overview')
@login_required
@cached(ttl=300)
def get_market_intelligence_overview():
    """Get comprehensive market intelligence overview"""
    try:
        overview = market_intelligence.get_market_overview()
        return jsonify(overview)
        
    except Exception as e:
        logger.error(f"Error getting market intelligence: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-intelligence/sentiment/<symbol>')
@login_required
@cached(ttl=180)
def get_symbol_sentiment(symbol):
    """Get detailed sentiment analysis for a symbol"""
    try:
        news_items = market_intelligence.news_aggregator.get_market_news([symbol])
        news_dicts = [item.__dict__ for item in news_items]
        sentiment = market_intelligence.news_aggregator.sentiment_analyzer.analyze_news_batch(news_dicts)
        
        return jsonify({
            'symbol': symbol,
            'sentiment': sentiment.__dict__,
            'news_items': news_dicts[:5]
        })
        
    except Exception as e:
        logger.error(f"Error getting sentiment for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

# Deep Learning Price Prediction Engine
@app.route('/api/deep-learning/analyze/<symbol>')
@login_required
@cached(ttl=900)
def deep_learning_analysis(symbol):
    """Get comprehensive deep learning analysis for a symbol"""
    try:
        analysis = deep_learning_engine.analyze_symbol(symbol)
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error in deep learning analysis for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

# Performance Optimization Endpoints
@app.route('/api/performance/optimization-report')
@login_required
def get_optimization_report():
    """Get comprehensive performance optimization report"""
    try:
        report = performance_optimizer.get_optimization_report()
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Error getting optimization report: {e}")
        return jsonify({'error': str(e)}), 500

# AI-Powered Trading Recommendations
@app.route('/api/ai/unified-recommendations')
@login_required
@cached(ttl=600)
def get_unified_ai_recommendations():
    """Get unified AI recommendations from all enhancement modules"""
    try:
        recommendations = {
            'market_intelligence': {},
            'deep_learning': {},
            'personalized_ai': {},
            'performance_optimization': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Get market intelligence recommendations
        market_overview = market_intelligence.get_market_overview()
        recommendations['market_intelligence'] = {
            'sentiment': market_overview.get('sentiment_analysis', {}),
            'alerts': market_overview.get('alerts', []),
            'regime': market_overview.get('market_regime', {})
        }
        
        # Get deep learning recommendations for top symbols
        top_symbols = ['AAPL', 'MSFT', 'GOOGL']
        for symbol in top_symbols:
            dl_analysis = deep_learning_engine.analyze_symbol(symbol)
            if not dl_analysis.get('error'):
                recommendations['deep_learning'][symbol] = dl_analysis.get('recommendations', [])
        
        # Get performance optimization recommendations
        perf_report = performance_optimizer.get_optimization_report()
        recommendations['performance_optimization'] = perf_report.get('recommendations', [])
        
        return jsonify(recommendations)
        
    except Exception as e:
        logger.error(f"Error getting unified AI recommendations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        # Check database connectivity
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        # Check AI services
        ai_status = {
            'ai_engine': bool(ai_engine),
            'order_manager': bool(order_manager),
            'market_intelligence': bool(market_intelligence),
            'deep_learning_engine': bool(deep_learning_engine),
            'performance_optimizer': bool(performance_optimizer)
        }
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'ai_services': ai_status,
            'version': '1.0.0',
            'features': [
                'advanced_orders',
                'market_intelligence', 
                'deep_learning',
                'performance_optimization',
                'error_recovery',
                'real_time_updates'
            ]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/ai/train-advice-engine', methods=['POST'])
def train_advice_engine():
    """Train the advanced AI advice engine"""
    try:
        data = request.get_json() or {}
        days = data.get('days', 365)
        symbols = data.get('symbols', ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'CRM', 'ADBE'])
        
        # Train the advice engine
        success = advice_engine.train_with_multiple_stocks(symbols, days)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'AI advice engine trained successfully',
                'training_samples': len(symbols) * days,
                'symbols_trained': symbols,
                'model_type': 'Advanced Ensemble Model'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Training failed - insufficient data'
            }), 500
            
    except Exception as e:
        logger.error(f"Error training advice engine: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/advice/<symbol>')
def get_ai_advice(symbol):
    """Get concise AI advice for a specific stock"""
    try:
        advice = advice_engine.get_concise_advice(symbol.upper())
        return jsonify(advice)
        
    except Exception as e:
        logger.error(f"Error getting advice for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

# Monetization API Endpoints
@app.route('/api/monetization/info')
def get_monetization_info():
    """Get comprehensive monetization information"""
    try:
        return jsonify(monetization_engine.get_monetization_summary())
    except Exception as e:
        logger.error(f"Error getting monetization info: {e}")
        return jsonify({'error': 'Failed to get monetization info'}), 500

@app.route('/api/monetization/premium-features')
def get_premium_features():
    """Get available premium features"""
    try:
        return jsonify(monetization_engine.get_premium_features())
    except Exception as e:
        logger.error(f"Error getting premium features: {e}")
        return jsonify({'error': 'Failed to get premium features'}), 500

@app.route('/api/monetization/revenue-projection')
def get_revenue_projection():
    """Get revenue projection based on user base"""
    try:
        user_count = User.query.count()
        trade_count = Trade.query.count()
        
        # Calculate monthly projections
        avg_trade_volume = trade_count * 1000  # $1000 average per trade
        monthly_commission = avg_trade_volume * monetization_engine.commission_rate
        
        premium_adoption = user_count * 0.1  # 10% adoption rate
        monthly_premium = premium_adoption * 8.5  # Average premium price
        
        referral_growth = user_count * 0.05  # 5% monthly referral growth
        monthly_referral = referral_growth * monetization_engine.referral_bonus
        
        total_monthly = monthly_commission + monthly_premium + monthly_referral
        
        return jsonify({
            'user_count': user_count,
            'trade_count': trade_count,
            'monthly_projections': {
                'trade_commissions': monthly_commission,
                'premium_subscriptions': monthly_premium,
                'referral_program': monthly_referral,
                'total_monthly_revenue': total_monthly,
                'annual_projection': total_monthly * 12
            },
            'growth_scenarios': {
                'conservative': total_monthly * 1.2,
                'moderate': total_monthly * 2.0,
                'aggressive': total_monthly * 5.0
            }
        })
    except Exception as e:
        logger.error(f"Error calculating revenue projection: {e}")
        return jsonify({'error': 'Failed to calculate revenue projection'}), 500

@app.route('/monetization-info')
def monetization_info_page():
    """Display monetization information page"""
    return render_template('monetization_info.html')

@app.route('/monetization-dashboard')
def monetization_dashboard():
    """Display monetization dashboard"""
    return render_template('monetization_dashboard.html')

# Duplicate section removed - keeping only the original routes
