from flask import render_template, jsonify, request, session, redirect, url_for
from app import app, db
from models import Trade, Portfolio, Alert, UserAccount, Transaction
from ai_insights import AIInsightsEngine
from data_service import DataService
import logging
import os
import stripe
from datetime import datetime

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# For demo purposes, create a default user account
DEFAULT_USER_ID = "demo_user_001"

logger = logging.getLogger(__name__)

# Initialize services
data_service = DataService()
ai_engine = AIInsightsEngine()

# Train AI model on startup
stocks_data = data_service.get_all_stocks()
ai_engine.train_model(stocks_data)

# Initialize default user account
def get_or_create_user_account():
    """Get or create default user account"""
    user_account = UserAccount.query.filter_by(user_id=DEFAULT_USER_ID).first()
    if not user_account:
        user_account = UserAccount(user_id=DEFAULT_USER_ID, balance=0.0)
        db.session.add(user_account)
        db.session.commit()
    return user_account

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/dashboard')
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

@app.route('/api/trade', methods=['POST'])
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
            symbol=data['symbol'].upper(),
            action=data['action'].lower(),
            quantity=data['quantity'],
            price=stock['current_price'],
            confidence_score=insights['confidence_score'],
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
def get_portfolio():
    """Get portfolio data"""
    try:
        portfolio_items = Portfolio.query.all()
        stocks = data_service.get_all_stocks()
        
        # Calculate current values
        portfolio_data = []
        total_value = 0
        total_cost = 0
        
        for item in portfolio_items:
            # Find current stock price
            current_stock = next((s for s in stocks if s['symbol'] == item.symbol), None)
            if current_stock:
                current_value = item.quantity * current_stock['current_price']
                cost_basis = item.quantity * item.avg_price
                pnl = current_value - cost_basis
                pnl_pct = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
                
                portfolio_data.append({
                    'symbol': item.symbol,
                    'quantity': item.quantity,
                    'avg_price': item.avg_price,
                    'current_price': current_stock['current_price'],
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
def get_sectors():
    """Get available sectors"""
    try:
        sectors = data_service.get_sectors()
        return jsonify({'sectors': sectors})
    except Exception as e:
        logger.error(f"Error getting sectors: {e}")
        return jsonify({'error': 'Failed to load sectors'}), 500

@app.route('/api/performance')
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
    portfolio_item = Portfolio.query.filter_by(symbol=trade.symbol).first()
    
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
        trades = Trade.query.all()
        
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
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
        
        win_rate = (winning_trades / max(winning_trades + losing_trades, 1)) * 100
        avg_confidence = total_confidence / total_trades
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
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

# AI Assistant Routes
@app.route('/api/ai/chat', methods=['POST'])
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

@app.route('/api/account/balance')
def get_account_balance():
    """Get user account balance"""
    try:
        user_account = get_or_create_user_account()
        return jsonify({
            'balance': user_account.balance,
            'total_deposited': user_account.total_deposited,
            'total_withdrawn': user_account.total_withdrawn
        })
    except Exception as e:
        logger.error(f"Error getting account balance: {e}")
        return jsonify({'error': 'Failed to get account balance'}), 500

@app.route('/api/create-deposit-session', methods=['POST'])
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
                'user_id': DEFAULT_USER_ID,
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
                user_id=DEFAULT_USER_ID,
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

@app.route('/api/purchase-stock', methods=['POST'])
def purchase_stock():
    """Purchase stock with account balance"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        quantity = int(data.get('quantity', 0))
        
        if not symbol or quantity <= 0:
            return jsonify({'error': 'Invalid stock symbol or quantity'}), 400
        
        # Get stock data
        stock_data = data_service.get_stock_by_symbol(symbol)
        if not stock_data:
            return jsonify({'error': 'Stock not found'}), 404
        
        price = stock_data['price']
        total_cost = price * quantity
        
        # Check account balance
        user_account = get_or_create_user_account()
        if user_account.balance < total_cost:
            return jsonify({'error': 'Insufficient funds'}), 400
        
        # Deduct from account balance
        user_account.balance -= total_cost
        
        # Create transaction record
        transaction = Transaction(
            user_id=DEFAULT_USER_ID,
            transaction_type='stock_purchase',
            amount=total_cost,
            symbol=symbol,
            quantity=quantity,
            price_per_share=price,
            status='completed'
        )
        
        # Create trade record
        trade = Trade(
            symbol=symbol,
            action='buy',
            quantity=quantity,
            price=price,
            confidence_score=0.8,  # Default confidence for manual purchases
            is_simulated=False
        )
        
        db.session.add(transaction)
        db.session.add(trade)
        
        # Update portfolio
        update_portfolio(trade)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully purchased {quantity} shares of {symbol}',
            'transaction_id': transaction.id,
            'remaining_balance': user_account.balance
        })
        
    except Exception as e:
        logger.error(f"Error purchasing stock: {e}")
        return jsonify({'error': 'Failed to purchase stock'}), 500

@app.route('/api/sell-stock', methods=['POST'])
def sell_stock():
    """Sell stock and add to account balance"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        quantity = int(data.get('quantity', 0))
        
        if not symbol or quantity <= 0:
            return jsonify({'error': 'Invalid stock symbol or quantity'}), 400
        
        # Check portfolio holdings
        portfolio_item = Portfolio.query.filter_by(symbol=symbol).first()
        if not portfolio_item or portfolio_item.quantity < quantity:
            return jsonify({'error': 'Insufficient shares to sell'}), 400
        
        # Get current stock price
        stock_data = data_service.get_stock_by_symbol(symbol)
        if not stock_data:
            return jsonify({'error': 'Stock not found'}), 404
        
        price = stock_data['price']
        total_proceeds = price * quantity
        
        # Add to account balance
        user_account = get_or_create_user_account()
        user_account.balance += total_proceeds
        
        # Create transaction record
        transaction = Transaction(
            user_id=DEFAULT_USER_ID,
            transaction_type='stock_sale',
            amount=total_proceeds,
            symbol=symbol,
            quantity=quantity,
            price_per_share=price,
            status='completed'
        )
        
        # Create trade record
        trade = Trade(
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
def get_transactions():
    """Get user transaction history"""
    try:
        transactions = Transaction.query.filter_by(user_id=DEFAULT_USER_ID).order_by(Transaction.created_at.desc()).limit(50).all()
        return jsonify([transaction.to_dict() for transaction in transactions])
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        return jsonify({'error': 'Failed to get transactions'}), 500
