#!/usr/bin/env python3
"""Fix missing portfolio entries"""

from app import app, db
from models import Portfolio, Trade

with app.app_context():
    # Check if there are any portfolio entries
    portfolios = Portfolio.query.all()
    print(f'Total portfolio entries: {len(portfolios)}')
    
    # Check trades
    trades = Trade.query.all()
    print(f'Total trades: {len(trades)}')
    for trade in trades:
        print(f'  Trade: {trade.symbol} - {trade.action} - {trade.quantity} shares @ ${trade.price}')
    
    # Fix missing portfolio entry from RMBS trade
    rmbs_trade = Trade.query.filter_by(symbol='RMBS', action='buy').first()
    if rmbs_trade:
        # Check if portfolio entry exists
        portfolio_entry = Portfolio.query.filter_by(user_id=rmbs_trade.user_id, symbol='RMBS').first()
        if not portfolio_entry:
            print(f'Creating portfolio entry for RMBS...')
            portfolio_entry = Portfolio(
                user_id=rmbs_trade.user_id,
                symbol='RMBS',
                quantity=rmbs_trade.quantity,
                avg_price=rmbs_trade.price
            )
            db.session.add(portfolio_entry)
            db.session.commit()
            print('Portfolio entry created!')
        else:
            print('Portfolio entry already exists for RMBS')