#!/usr/bin/env python3
"""
Create a Pro test user for subscription tier testing
"""

from app import app, db
from models import User, UserAccount
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def create_pro_test_user():
    """Create a test user with Pro subscription"""
    with app.app_context():
        # Create or update pro test user
        user = User.query.filter_by(username='pro_test').first()
        if not user:
            user = User(
                username='pro_test',
                email='pro_test@example.com',
                password_hash=generate_password_hash('test123')
            )
            db.session.add(user)
            db.session.commit()
            print(f"✅ Created Pro test user: {user.username}")
        else:
            print(f"✅ Pro test user already exists: {user.username}")
        
        # Update user subscription
        user.subscription_type = 'pro'
        user.subscription_expires = datetime.utcnow() + timedelta(days=30)
        user.subscription_created = datetime.utcnow()
        
        # Create or update user account
        account = UserAccount.query.filter_by(user_id=user.id).first()
        if not account:
            account = UserAccount(
                user_id=user.id,
                balance=10000.0  # $10,000 starting balance
            )
            db.session.add(account)
        else:
            account.balance = 10000.0
        
        db.session.commit()
        
        print(f"✅ Pro subscription configured:")
        print(f"   Plan: {user.subscription_type}")
        print(f"   Expires: {user.subscription_expires}")
        print(f"   Balance: ${account.balance:,.2f}")
        
        print("\n🔐 Pro Test Credentials:")
        print("   Username: pro_test")
        print("   Password: test123")
        print("\n📋 How to test:")
        print("1. Log out of current account")
        print("2. Log in with pro_test / test123")
        print("3. View subscription modal to see Pro tier UI")
        print("4. Check AI Copilot features (should be limited compared to Elite)")

if __name__ == "__main__":
    create_pro_test_user()