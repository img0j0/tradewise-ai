#!/usr/bin/env python3
"""
Direct login helper for portfolio testing
"""
from app import app
from models import User
from flask import session
from flask_login import login_user
import requests

def test_direct_login():
    """Test direct login and portfolio access"""
    print("🔐 TESTING DIRECT LOGIN AND PORTFOLIO ACCESS")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Get demo user
            demo_user = User.query.filter_by(username='demo').first()
            if not demo_user:
                print("❌ Demo user not found")
                return
                
            print(f"✅ Demo user found: {demo_user.username}")
            
            # Test login endpoint
            login_data = {
                'username': 'demo',
                'password': 'demo123'
            }
            
            # Create session for testing
            with app.test_client() as client:
                # Login
                response = client.post('/login', data=login_data, follow_redirects=False)
                print(f"Login response: {response.status_code}")
                
                if response.status_code in [200, 302]:
                    print("✅ Login successful")
                    
                    # Test portfolio access
                    portfolio_response = client.get('/portfolio', follow_redirects=False)
                    print(f"Portfolio response: {portfolio_response.status_code}")
                    
                    if portfolio_response.status_code == 200:
                        content = portfolio_response.get_data(as_text=True)
                        if 'Enhanced Portfolio' in content:
                            print("✅ Enhanced portfolio template loading")
                        elif 'portfolio-header' in content:
                            print("✅ Direct enhanced portfolio working")
                        else:
                            print("❌ Old template still loading")
                            print(f"Content preview: {content[:200]}...")
                    else:
                        print(f"❌ Portfolio access failed: {portfolio_response.status_code}")
                else:
                    print("❌ Login failed")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_direct_login()