#!/usr/bin/env python3
"""
Create a Free test user for subscription tier testing
"""

from app import app, db
from models import User, UserAccount
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def create_free_test_user():
    """Create a test user with Free subscription"""
    with app.app_context():
        # Create or update free test user
        user = User.query.filter_by(username='free_test').first()
        if not user:
            user = User(
                username='free_test',
                email='free_test@example.com',
                password_hash=generate_password_hash('test123')
            )
            db.session.add(user)
            db.session.commit()
            print(f"✅ Created Free test user: {user.username}")
        else:
            print(f"✅ Free test user already exists: {user.username}")
        
        # Update user subscription
        user.subscription_type = 'free'
        user.subscription_expires = None
        user.subscription_created = None
        
        # Create or update user account
        account = UserAccount.query.filter_by(user_id=user.id).first()
        if not account:
            account = UserAccount(
                user_id=user.id,
                balance=1000.0  # $1,000 starting balance
            )
            db.session.add(account)
        else:
            account.balance = 1000.0
        
        db.session.commit()
        
        print(f"✅ Free subscription configured:")
        print(f"   Plan: {user.subscription_type}")
        print(f"   Expires: {user.subscription_expires}")
        print(f"   Balance: ${account.balance:,.2f}")
        
        print("\n🔐 Free Test Credentials:")
        print("   Username: free_test")
        print("   Password: test123")
        print("\n📋 How to test:")
        print("1. Log out of current account")
        print("2. Log in with free_test / test123")
        print("3. View subscription modal to see Free tier UI")
        print("4. Check that AI Copilot is hidden for free users")
        print("5. Verify upgrade buttons are visible")

if __name__ == "__main__":
    create_free_test_user()