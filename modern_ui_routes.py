"""
Modern UI Routes
Routes for the new modern SaaS interface
"""

from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import login_required, current_user
import logging

logger = logging.getLogger(__name__)

# Create blueprint
modern_ui_bp = Blueprint('modern_ui', __name__)

@modern_ui_bp.route('/dashboard')
def dashboard():
    """Modern dashboard page"""
    try:
        return render_template('modern_dashboard.html')
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template('error_500.html'), 500

@modern_ui_bp.route('/search')
def search():
    """Modern search page"""
    try:
        return render_template('modern_search.html')
    except Exception as e:
        logger.error(f"Search page error: {e}")
        return render_template('error_500.html'), 500

@modern_ui_bp.route('/portfolio')
def portfolio():
    """Modern portfolio page"""
    try:
        return render_template('modern_portfolio.html')
    except Exception as e:
        logger.error(f"Portfolio page error: {e}")
        return render_template('error_500.html'), 500

@modern_ui_bp.route('/backtest')
def backtest():
    """Modern backtesting page"""
    try:
        return render_template('modern_backtest.html')
    except Exception as e:
        logger.error(f"Backtest page error: {e}")
        return render_template('error_500.html'), 500

@modern_ui_bp.route('/peer-comparison')
def peer_comparison():
    """Modern peer comparison page"""
    try:
        return render_template('modern_peer_comparison.html')
    except Exception as e:
        logger.error(f"Peer comparison page error: {e}")
        return render_template('error_500.html'), 500

@modern_ui_bp.route('/scanner')
def scanner():
    """Modern market scanner page"""
    try:
        return render_template('modern_scanner.html')
    except Exception as e:
        logger.error(f"Scanner page error: {e}")
        return render_template('error_500.html'), 500

@modern_ui_bp.route('/watchlist')
def watchlist():
    """Modern watchlist page"""
    try:
        return render_template('modern_watchlist.html')
    except Exception as e:
        logger.error(f"Watchlist page error: {e}")
        return render_template('error_500.html'), 500

@modern_ui_bp.route('/alerts')
def alerts():
    """Modern alerts page"""
    try:
        return render_template('modern_alerts.html')
    except Exception as e:
        logger.error(f"Alerts page error: {e}")
        return render_template('error_500.html'), 500

@modern_ui_bp.route('/settings')
def settings():
    """Modern settings page"""
    try:
        return render_template('modern_settings.html')
    except Exception as e:
        logger.error(f"Settings page error: {e}")
        return render_template('error_500.html'), 500

# Export blueprint
__all__ = ['modern_ui_bp']