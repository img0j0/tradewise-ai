from flask import Blueprint, request, jsonify, session
from datetime import datetime
import logging
from portfolio_manager import PortfolioManager
import uuid

logger = logging.getLogger(__name__)

# Create portfolio blueprint
portfolio_bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolio')

# Initialize portfolio manager
portfolio_manager = PortfolioManager()

def get_user_id():
    """Get user ID from session (for demo purposes)"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

@portfolio_bp.route('/add', methods=['POST'])
def add_holding():
    """Add a new stock holding to user's portfolio"""
    try:
        data = request.get_json()
        user_id = get_user_id()
        
        # Validate required fields
        required_fields = ['symbol', 'shares', 'purchase_price']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}',
                    'message': 'Please provide all required information'
                }), 400
        
        # Extract data
        symbol = data['symbol'].strip().upper()
        shares = float(data['shares'])
        purchase_price = float(data['purchase_price'])
        purchase_date = data.get('purchase_date')
        notes = data.get('notes', '')
        
        # Validate values
        if shares <= 0:
            return jsonify({
                'success': False,
                'error': 'Invalid shares amount',
                'message': 'Shares must be greater than 0'
            }), 400
        
        if purchase_price <= 0:
            return jsonify({
                'success': False,
                'error': 'Invalid purchase price',
                'message': 'Purchase price must be greater than 0'
            }), 400
        
        # Add holding
        result = portfolio_manager.add_holding(
            user_id=user_id,
            symbol=symbol,
            shares=shares,
            purchase_price=purchase_price,
            purchase_date=purchase_date
        )
        
        logger.info(f"Adding holding: {symbol} ({shares} shares) for user {user_id}")
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid number format',
            'message': 'Please check your shares and price values'
        }), 400
    except Exception as e:
        logger.error(f"Error adding holding: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to add holding',
            'message': 'Please try again or contact support'
        }), 500

@portfolio_bp.route('/remove', methods=['POST'])
def remove_holding():
    """Remove or reduce shares from a holding"""
    try:
        data = request.get_json()
        user_id = get_user_id()
        
        # Validate required fields
        if 'symbol' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing symbol',
                'message': 'Please provide the stock symbol'
            }), 400
        
        symbol = data['symbol'].strip().upper()
        shares = data.get('shares')
        
        if shares is not None:
            shares = float(shares)
            if shares <= 0:
                return jsonify({
                    'success': False,
                    'error': 'Invalid shares amount',
                    'message': 'Shares must be greater than 0'
                }), 400
        
        # Remove holding
        result = portfolio_manager.remove_holding(
            user_id=user_id,
            symbol=symbol,
            shares=shares
        )
        
        logger.info(f"Removing holding: {symbol} for user {user_id}")
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid number format',
            'message': 'Please check your shares value'
        }), 400
    except Exception as e:
        logger.error(f"Error removing holding: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to remove holding',
            'message': 'Please try again or contact support'
        }), 500

@portfolio_bp.route('/summary', methods=['GET'])
def get_portfolio_summary():
    """Get comprehensive portfolio summary"""
    try:
        user_id = get_user_id()
        
        # Get portfolio summary
        result = portfolio_manager.get_portfolio_summary(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get portfolio summary',
            'message': 'Please try again or contact support'
        }), 500

@portfolio_bp.route('/analytics', methods=['GET'])
def get_portfolio_analytics():
    """Get advanced portfolio analytics and risk metrics"""
    try:
        user_id = get_user_id()
        
        # Get portfolio analytics
        result = portfolio_manager.get_portfolio_analytics(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error getting portfolio analytics: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get portfolio analytics',
            'message': 'Please try again or contact support'
        }), 500

@portfolio_bp.route('/holdings', methods=['GET'])
def get_holdings():
    """Get all portfolio holdings"""
    try:
        user_id = get_user_id()
        
        # Get portfolio summary which includes holdings
        result = portfolio_manager.get_portfolio_summary(user_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'holdings': result['holdings'],
                'total_holdings': result['total_holdings'],
                'last_updated': result['last_updated']
            }), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error getting holdings: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get holdings',
            'message': 'Please try again or contact support'
        }), 500

@portfolio_bp.route('/holding/<symbol>', methods=['GET'])
def get_holding_details(symbol):
    """Get detailed information for a specific holding"""
    try:
        user_id = get_user_id()
        symbol = symbol.upper()
        
        # Get portfolio summary and filter for specific holding
        result = portfolio_manager.get_portfolio_summary(user_id)
        
        if result['success']:
            holding = next((h for h in result['holdings'] if h['symbol'] == symbol), None)
            if holding:
                return jsonify({
                    'success': True,
                    'holding': holding
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Holding not found',
                    'message': f'You do not have {symbol} in your portfolio'
                }), 404
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error getting holding details for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get holding details',
            'message': 'Please try again or contact support'
        }), 500

@portfolio_bp.route('/performance', methods=['GET'])
def get_portfolio_performance():
    """Get portfolio performance metrics over time"""
    try:
        user_id = get_user_id()
        
        # Get analytics which includes performance data
        result = portfolio_manager.get_portfolio_analytics(user_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'performance': result['analytics']['performance_metrics'],
                'risk_metrics': result['analytics']['risk_metrics']
            }), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error getting portfolio performance: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get portfolio performance',
            'message': 'Please try again or contact support'
        }), 500