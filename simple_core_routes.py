from flask import Blueprint, render_template, jsonify, request, make_response, redirect, url_for
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create simple core routes blueprint
simple_core_bp = Blueprint('simple_core', __name__)

@simple_core_bp.route('/')
def index():
    """Redirect to dashboard"""
    return redirect(url_for('simple_core.dashboard'))

@simple_core_bp.route('/dashboard')
def dashboard():
    """Dashboard - Exact Design Match"""
    try:
        return render_template('dashboard_exact.html')
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return f"Dashboard error: {str(e)}", 500

@simple_core_bp.route('/search')
def search():
    """Modern Search Interface"""
    try:
        return render_template('modern_search_new.html')
    except Exception as e:
        logger.error(f"Error loading search page: {e}")
        return f"Search error: {str(e)}", 500

@simple_core_bp.route('/premium/upgrade')
def premium_upgrade():
    """Premium upgrade page"""
    try:
        return render_template('premium_upgrade_new.html')
    except Exception as e:
        logger.error(f"Error loading premium page: {e}")
        return f"Premium page error: {str(e)}", 500

@simple_core_bp.route('/api/user/plan')
def get_user_plan():
    """Get current user's subscription plan"""
    return jsonify({'plan': 'free', 'features': ['basic_search', 'limited_analysis']})

@simple_core_bp.route('/api/portfolio/summary')
def get_portfolio_summary():
    """Get portfolio summary data for dashboard"""
    return jsonify({
        'totalValue': 125420.50,
        'change': 2847.32,
        'changePercent': 2.34,
        'sparklineData': [100000, 102000, 98000, 105000, 110000, 108000, 115000, 120000, 125420]
    })

@simple_core_bp.route('/api/market/overview')
def get_market_overview():
    """Get market overview data"""
    return jsonify({
        'indices': {
            'sp500': {'value': 5847.87, 'change': 0.8},
            'nasdaq': {'value': 19630.20, 'change': 1.2},
            'dow': {'value': 43239.05, 'change': -0.3}
        },
        'sectors': {
            'technology': 2.4,
            'healthcare': 1.8,
            'finance': -0.5,
            'energy': 3.2,
            'consumer': 1.1,
            'industrial': 0.8
        }
    })

@simple_core_bp.route('/api/market-data')
def market_data():
    """Simple market data endpoint for dashboard"""
    return jsonify({
        'portfolio': {
            'value': 125430.50,
            'change': 2.34,
            'change_percent': 1.89
        },
        'top_stocks': [
            {'symbol': 'AAPL', 'price': 191.45, 'change': 1.23},
            {'symbol': 'MSFT', 'price': 378.42, 'change': -0.87},
            {'symbol': 'NVDA', 'price': 442.73, 'change': 5.12}
        ],
        'market_status': 'open'
    })

@simple_core_bp.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200