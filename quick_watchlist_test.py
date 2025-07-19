#!/usr/bin/env python3
"""
Quick test for watchlist functionality
"""
from app import app
from routes import watchlist_manager
import json

def quick_test():
    with app.app_context():
        # Test with existing user ID 5 (demo_user)
        user_id = 5
        
        print(f"Testing watchlist for user ID: {user_id}")
        
        # Test adding to watchlist
        try:
            result = watchlist_manager.add_to_watchlist(user_id, 'My Portfolio', 'AAPL')
            print(f"Add result: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"Error adding to watchlist: {e}")
        
        # Test getting watchlists 
        try:
            result = watchlist_manager.get_user_watchlists(user_id)
            print(f"Get result success: {result.get('success', False)}")
            if result.get('success'):
                print(f"Total symbols: {result.get('total_symbols', 0)}")
                for name, items in result.get('watchlists', {}).items():
                    print(f"  {name}: {len(items)} items")
        except Exception as e:
            print(f"Error getting watchlists: {e}")

if __name__ == '__main__':
    quick_test()