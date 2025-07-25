"""Simple page routes for the modern SaaS interface"""
from flask import Blueprint, render_template
from routes import main_bp

@main_bp.route('/dashboard')
def dashboard():
    """Modern SaaS Dashboard"""
    return render_template('modern_dashboard.html')

@main_bp.route('/search')
def search():
    """Stock Search Interface"""
    return render_template('modern_search.html')

@main_bp.route('/backtest')
def backtest():
    """Portfolio Backtesting Interface"""
    return render_template('modern_backtest.html')

@main_bp.route('/portfolio')
def portfolio():
    """Portfolio Management Interface"""
    return render_template('modern_dashboard.html')  # Using dashboard for now