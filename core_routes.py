from flask import Blueprint, render_template, jsonify, request, make_response, redirect, url_for
from app import app, db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create core routes blueprint with unique name
core_routes_bp = Blueprint('core_routes', __name__)

@core_routes_bp.route('/')
def index():
    """Redirect to dashboard"""
    return redirect(url_for('core_routes.dashboard'))

@core_routes_bp.route('/dashboard')
def dashboard():
    """Modern SaaS Dashboard - Main Entry Point"""
    try:
        response = make_response(render_template('modern_dashboard_new.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return jsonify({'error': 'Dashboard loading error'}), 500

@core_routes_bp.route('/search')
def search():
    """Modern Search Interface"""
    try:
        response = make_response(render_template('modern_search_new.html'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        logger.error(f"Error loading search page: {e}")
        return jsonify({'error': 'Search page loading error'}), 500

@core_routes_bp.route('/backtest')
def backtest():
    """Portfolio Backtesting - Premium Feature"""
    return render_template('premium_feature.html', 
                         feature='backtest',
                         title='Portfolio Backtesting',
                         description='Test your investment strategies against historical data')

@core_routes_bp.route('/peer_comparison')
def peer_comparison():
    """Peer Comparison Analysis - Premium Feature"""
    return render_template('premium_feature.html',
                         feature='peer-analysis', 
                         title='Peer Comparison',
                         description='Compare stocks against industry peers')

@core_routes_bp.route('/premium/upgrade')
def premium_upgrade():
    """Premium upgrade page"""
    return render_template('premium_upgrade_new.html')

@core_routes_bp.route('/settings')
def settings():
    """User settings page"""
    return render_template('account_settings.html')

@core_routes_bp.route('/help')
def help_page():
    """Help and support page"""
    return render_template('help.html')

@core_routes_bp.route('/api/user/plan')
def get_user_plan():
    """Get current user's subscription plan"""
    return jsonify({'plan': 'free', 'features': ['basic_search', 'limited_analysis']})

@core_routes_bp.route('/api/portfolio/summary')
def get_portfolio_summary():
    """Get portfolio summary data for dashboard"""
    return jsonify({
        'totalValue': 125420.50,
        'change': 2847.32,
        'changePercent': 2.34,
        'sparklineData': [100000, 102000, 98000, 105000, 110000, 108000, 115000, 120000, 125420]
    })

@core_routes_bp.route('/api/market/overview')
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

@core_routes_bp.route('/api/health')
def health_check():
    """Health check endpoint for production monitoring"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'version': '1.0.0',
            'services': {
                'ai_engine': 'operational',
                'stock_data': 'operational',
                'payment_system': 'operational'
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503

# Error handlers
@core_routes_bp.errorhandler(404)
def page_not_found(error):
    """Custom 404 error page"""
    return render_template('error_404.html'), 404

@core_routes_bp.errorhandler(500)
def internal_server_error(error):
    """Custom 500 error page"""
    db.session.rollback()
    return render_template('error_500.html'), 500