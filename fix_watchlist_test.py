#!/usr/bin/env python3
"""
Test script to fix watchlist functionality
"""
from app import app, db
from models import User
from watchlist_manager import WatchlistManager

def test_watchlist_functionality():
    with app.app_context():
        # Use existing demo_user (ID 5)
        user = User.query.filter_by(username='demo_user').first()
        if not user:
            print("Demo user not found")
            return
        
        print(f"Using user: {user.username} (ID: {user.id})")
        
        # Test watchlist manager
        wm = WatchlistManager()
        
        # Test getting watchlists
        result = wm.get_user_watchlists(user.id)
        print(f"Get watchlists result: {result}")
        
        # Test adding to watchlist
        add_result = wm.add_to_watchlist(user.id, 'My Portfolio', 'AAPL')
        print(f"Add AAPL result: {add_result}")
        
        # Test getting watchlists again
        result2 = wm.get_user_watchlists(user.id)
        print(f"Get watchlists after adding AAPL: {result2}")

if __name__ == '__main__':
    test_watchlist_functionality()