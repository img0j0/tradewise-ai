#!/usr/bin/env python3
"""Create a test user for the trading analytics platform"""

from app import app, db
from models import User, UserAccount
from werkzeug.security import generate_password_hash

def create_test_user():
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            print('Test user already exists!')
            print('Username: testuser')
            print('Password: password123')
            return
        
        # Create a test user
        test_user = User()
        test_user.username = 'testuser'
        test_user.email = 'test@example.com'
        test_user.password_hash = generate_password_hash('password123')
        
        db.session.add(test_user)
        db.session.commit()
        
        # Create user account with starting balance
        user_account = UserAccount()
        user_account.user_id = test_user.id
        user_account.balance = 10000.0  # $10,000 starting balance
        user_account.total_deposited = 10000.0
        
        db.session.add(user_account)
        db.session.commit()
        
        print('Test user created successfully!')
        print('Username: testuser')
        print('Password: password123')
        print('Starting balance: $10,000')

if __name__ == '__main__':
    create_test_user()