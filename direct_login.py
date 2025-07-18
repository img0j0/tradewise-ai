#!/usr/bin/env python3
"""
Direct Login Script - Bypass login for testing
"""

from app import app, db
from models import User
from flask_login import LoginManager, login_user
from werkzeug.security import generate_password_hash

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_quick_access_user():
    """Create a quick access user for testing"""
    with app.app_context():
        # Check if demo user exists
        demo_user = User.query.filter_by(username='demo').first()
        
        if not demo_user:
            # Create demo user with simple password
            demo_user = User(
                username='demo',
                email='demo@example.com',
                password_hash=generate_password_hash('demo123')
            )
            db.session.add(demo_user)
            db.session.commit()
            print("Demo user created: demo / demo123")
        else:
            print("Demo user already exists: demo / demo123")
            
        return demo_user

def setup_login_bypass():
    """Setup login bypass for testing"""
    print("Setting up login bypass...")
    
    # Create demo user
    demo_user = create_quick_access_user()
    
    # Print available users
    with app.app_context():
        users = User.query.all()
        print("\nAvailable users:")
        print("================")
        for user in users:
            print(f"Username: {user.username} | Email: {user.email}")
        
        # Simple password hints
        print("\nLogin credentials:")
        print("================")
        print("Username: demo | Password: demo123")
        print("Username: testuser | Password: password123")
        print("Username: trader1 | Password: trader123")
        print("Username: ai_trader | Password: ai123")

if __name__ == "__main__":
    setup_login_bypass()