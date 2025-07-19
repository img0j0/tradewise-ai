#!/usr/bin/env python3
"""
Quick demo user creation for portfolio testing
"""
from app import app, db
from models import User, UserAccount, Portfolio
from werkzeug.security import generate_password_hash
import uuid

def create_demo_user():
    """Create a demo user for portfolio testing"""
    with app.app_context():
        try:
            # Check if demo user exists
            demo_user = User.query.filter_by(username='demo').first()
            if not demo_user:
                # Create demo user
                demo_user = User(
                    id=str(uuid.uuid4()),
                    username='demo',
                    email='demo@tradewise.ai',
                    password_hash=generate_password_hash('demo123'),
                    first_name='Demo',
                    last_name='User'
                )
                db.session.add(demo_user)
                
                # Create user account
                user_account = UserAccount(
                    user_id=demo_user.id,
                    balance=100000.00,  # $100K demo balance
                    subscription_tier='free'
                )
                db.session.add(user_account)
                
                # Create sample portfolio entry
                portfolio_entry = Portfolio(
                    user_id=demo_user.id,
                    symbol='AAPL',
                    quantity=50,
                    avg_price=185.30
                )
                db.session.add(portfolio_entry)
                
                db.session.commit()
                print("✅ Demo user created successfully")
                print("   Username: demo")
                print("   Password: demo123")
                print("   Portfolio: 50 shares of AAPL")
                print("   Balance: $100,000")
            else:
                print("✅ Demo user already exists")
                print("   Username: demo")
                print("   Password: demo123")
                
        except Exception as e:
            print(f"❌ Error creating demo user: {e}")
            db.session.rollback()

if __name__ == "__main__":
    create_demo_user()