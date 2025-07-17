#!/usr/bin/env python3
"""Check portfolio data"""

from app import app, db
from models import Portfolio, User

with app.app_context():
    # Check the logged in user's portfolio
    trader1 = User.query.filter_by(username='trader1').first()
    if trader1:
        print(f'User ID: {trader1.id}')
        portfolios = Portfolio.query.filter_by(user_id=trader1.id).all()
        print(f'Portfolio entries for trader1: {len(portfolios)}')
        for p in portfolios:
            print(f'  - {p.symbol}: {p.quantity} shares @ ${p.avg_price}')
    
    # Check all portfolios
    all_portfolios = Portfolio.query.all()
    print(f'\nTotal portfolio entries in database: {len(all_portfolios)}')
    for p in all_portfolios:
        print(f'  User {p.user_id}: {p.symbol} - {p.quantity} shares')