#!/usr/bin/env python3
"""Create a new test user with different credentials"""

from app import app, db
from models import User, UserAccount

# New user credentials
NEW_USERNAME = "trader1"
NEW_PASSWORD = "TradingPro2025"
NEW_EMAIL = "trader1@example.com"

with app.app_context():
    # Check if user already exists
    existing_user = User.query.filter_by(username=NEW_USERNAME).first()
    if existing_user:
        print(f"User '{NEW_USERNAME}' already exists. Deleting and recreating...")
        # Delete related records first
        UserAccount.query.filter_by(user_id=existing_user.id).delete()
        db.session.delete(existing_user)
        db.session.commit()
    
    # Create new user
    new_user = User(
        username=NEW_USERNAME,
        email=NEW_EMAIL
    )
    new_user.set_password(NEW_PASSWORD)
    
    # Add to database
    db.session.add(new_user)
    db.session.commit()
    
    # Create user account with starting balance
    user_account = UserAccount(
        user_id=new_user.id,
        balance=10000.0,  # $10,000 starting balance
        total_deposited=10000.0
    )
    db.session.add(user_account)
    db.session.commit()
    
    print(f"✓ New user created successfully!")
    print(f"  Username: {NEW_USERNAME}")
    print(f"  Password: {NEW_PASSWORD}")
    print(f"  Email: {NEW_EMAIL}")
    print(f"  Starting balance: $10,000")
    
    # Verify the user can login
    if new_user.check_password(NEW_PASSWORD):
        print("✓ Password verification successful")
    else:
        print("✗ Password verification failed")