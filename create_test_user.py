#!/usr/bin/env python3
"""
Create a test user for premium subscription testing
"""

from app import app, db
from models import User
import logging

def create_test_user():
    """Create a test user for premium subscription testing"""
    with app.app_context():
        # Check if test user already exists
        test_user = User.query.filter_by(username='premium_test').first()
        
        if test_user:
            print("✅ Test user 'premium_test' already exists")
            print(f"   - ID: {test_user.id}")
            print(f"   - Email: {test_user.email}")
            print(f"   - Premium: {getattr(test_user, 'subscription_type', 'free')}")
            return test_user
        
        # Create new test user
        test_user = User(
            username='premium_test',
            email='premium@test.com'
        )
        test_user.set_password('test123')
        
        # Add to database
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ Created test user 'premium_test'")
        print(f"   - Username: premium_test")
        print(f"   - Password: test123")
        print(f"   - Email: premium@test.com")
        print(f"   - ID: {test_user.id}")
        
        return test_user

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_test_user()
    print("\n🔑 Login credentials:")
    print("   Username: premium_test")
    print("   Password: test123")
    print("\n🧪 Test steps:")
    print("1. Go to http://localhost:5000")
    print("2. Login with credentials above")
    print("3. Click upgrade button")
    print("4. Subscribe to any plan")
    print("5. Watch for AI Copilot widget to appear")