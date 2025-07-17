#!/usr/bin/env python3
"""Fix trader1's portfolio"""

from app import app, db
from models import Portfolio, User, Trade

with app.app_context():
    # Get trader1 user
    trader1 = User.query.filter_by(username='trader1').first()
    if trader1:
        print(f'Fixing portfolio for trader1 (ID: {trader1.id})')
        
        # Check if trader1 has RMBS position
        rmbs_portfolio = Portfolio.query.filter_by(user_id=trader1.id, symbol='RMBS').first()
        if not rmbs_portfolio:
            # Create RMBS position for trader1
            rmbs_portfolio = Portfolio(
                user_id=trader1.id,
                symbol='RMBS',
                quantity=100,
                avg_price=66.79
            )
            db.session.add(rmbs_portfolio)
            print('  - Added RMBS position: 100 shares @ $66.79')
        
        # Add some more sample positions for a diversified portfolio
        sample_positions = [
            {'symbol': 'AAPL', 'quantity': 50, 'avg_price': 175.50},
            {'symbol': 'MSFT', 'quantity': 30, 'avg_price': 378.25},
            {'symbol': 'GOOGL', 'quantity': 20, 'avg_price': 138.75}
        ]
        
        for pos in sample_positions:
            existing = Portfolio.query.filter_by(user_id=trader1.id, symbol=pos['symbol']).first()
            if not existing:
                portfolio_item = Portfolio(
                    user_id=trader1.id,
                    symbol=pos['symbol'],
                    quantity=pos['quantity'],
                    avg_price=pos['avg_price']
                )
                db.session.add(portfolio_item)
                print(f'  - Added {pos["symbol"]} position: {pos["quantity"]} shares @ ${pos["avg_price"]}')
        
        # Also create corresponding trades for history
        if not Trade.query.filter_by(user_id=trader1.id).first():
            # Add RMBS trade
            rmbs_trade = Trade(
                user_id=trader1.id,
                symbol='RMBS',
                action='buy',
                quantity=100,
                price=66.79,
                confidence_score=0.8,
                is_simulated=False
            )
            db.session.add(rmbs_trade)
            print('  - Added RMBS trade to history')
        
        db.session.commit()
        print('\nPortfolio fixed successfully!')
        
        # Verify
        trader1_portfolio = Portfolio.query.filter_by(user_id=trader1.id).all()
        print(f'\nTrader1 now has {len(trader1_portfolio)} positions:')
        for p in trader1_portfolio:
            print(f'  - {p.symbol}: {p.quantity} shares @ ${p.avg_price}')