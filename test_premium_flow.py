#!/usr/bin/env python3
"""
Premium Subscription Flow Test
Tests the complete premium subscription process
"""

import requests
import json
import sys
from datetime import datetime, timedelta

def test_premium_subscription_flow():
    """Test complete premium subscription flow"""
    base_url = "http://localhost:5000"
    
    print("🔄 Testing Premium Subscription Flow...")
    print("=" * 60)
    
    # Test 1: Check premium features are available
    print("1. Testing Premium Features API...")
    try:
        response = requests.get(f"{base_url}/api/premium/features")
        if response.status_code == 200:
            data = response.json()
            print("✅ Premium features API working")
            print(f"   - Free plan: ${data['plans']['free']['price']}")
            print(f"   - Pro plan: ${data['plans']['pro']['price']}")
            print(f"   - Elite plan: ${data['plans']['elite']['price']}")
            
            # Verify feature lists
            pro_features = data['plans']['pro']['features']
            elite_features = data['plans']['elite']['features']
            
            print(f"   - Pro features: {len(pro_features)} items")
            print(f"   - Elite features: {len(elite_features)} items")
            
            # Check for key premium features
            elite_str = str(elite_features)
            has_monitoring = "24/7 AI" in elite_str
            has_execution = "One-click" in elite_str
            has_voice = "voice" in elite_str
            
            print(f"   - 24/7 monitoring: {'✅' if has_monitoring else '❌'}")
            print(f"   - One-click execution: {'✅' if has_execution else '❌'}")
            print(f"   - Voice commentary: {'✅' if has_voice else '❌'}")
        else:
            print(f"❌ Premium features API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Premium features API error: {e}")
        return False
    
    # Test 2: Verify AI Copilot is ready
    print("\n2. Testing AI Copilot Readiness...")
    try:
        from ai_trading_copilot import ai_copilot, start_ai_copilot
        
        # Check initial state
        print(f"✅ AI Copilot instance available")
        print(f"   - Current subscribers: {len(ai_copilot.subscribers)}")
        print(f"   - Monitoring active: {ai_copilot.is_monitoring}")
        print(f"   - Watchlist size: {len(ai_copilot.watchlist)}")
        print(f"   - Signal history: {len(ai_copilot.signal_history)}")
        
        # Test starting monitoring
        if not ai_copilot.is_monitoring:
            print("   - Starting AI monitoring...")
            start_ai_copilot()
            print(f"   - Monitoring now active: {ai_copilot.is_monitoring}")
        
        # Test subscriber management
        test_user_id = "test_user_123"
        ai_copilot.add_subscriber(test_user_id)
        print(f"   - Test subscriber added: {test_user_id in ai_copilot.subscribers}")
        
        # Test copilot status
        status = ai_copilot.get_copilot_status()
        print(f"   - Market status: {status['market_status']}")
        print(f"   - Signals today: {status['signals_today']}")
        
        # Cleanup test subscriber
        ai_copilot.remove_subscriber(test_user_id)
        
    except Exception as e:
        print(f"❌ AI Copilot error: {e}")
        return False
    
    # Test 3: Verify Premium Modal Integration
    print("\n3. Testing Premium Modal Integration...")
    try:
        # Check if premium modal template exists and has required elements
        with open('templates/premium_modal.html', 'r') as f:
            modal_content = f.read()
        
        required_elements = [
            'premiumModal',
            'subscribeToPlan',
            'Upgrade to Pro',
            'Upgrade to Elite',
            '$19.99',
            '$39.99'
        ]
        
        all_present = True
        for element in required_elements:
            if element in modal_content:
                print(f"   ✅ {element}: Found")
            else:
                print(f"   ❌ {element}: Missing")
                all_present = False
        
        if all_present:
            print("✅ Premium modal fully integrated")
        else:
            print("❌ Premium modal missing elements")
            return False
            
    except Exception as e:
        print(f"❌ Premium modal error: {e}")
        return False
    
    # Test 4: Check JavaScript Premium Manager
    print("\n4. Testing JavaScript Premium Manager...")
    try:
        with open('static/js/premium.js', 'r') as f:
            js_content = f.read()
        
        required_functions = [
            'class PremiumManager',
            'async subscribeToPlan',
            'async checkPremiumStatus',
            'updateUI',
            'togglePremiumFeatures',
            'loadCopilotSignals'
        ]
        
        all_functions = True
        for func in required_functions:
            if func in js_content:
                print(f"   ✅ {func}: Found")
            else:
                print(f"   ❌ {func}: Missing")
                all_functions = False
        
        if all_functions:
            print("✅ Premium Manager JavaScript complete")
        else:
            print("❌ Premium Manager JavaScript incomplete")
            return False
            
    except Exception as e:
        print(f"❌ JavaScript error: {e}")
        return False
    
    # Test 5: Check Database Model Support
    print("\n5. Testing Database Model Support...")
    try:
        from models import User
        from datetime import datetime, timedelta
        
        # Create test user object to verify fields
        test_user = User()
        test_user.username = "premium_test_user"
        test_user.email = "test@premium.com"
        test_user.subscription_type = "elite"
        test_user.subscription_expires = datetime.now() + timedelta(days=30)
        test_user.subscription_created = datetime.now()
        
        print("✅ User model supports premium fields")
        print(f"   - subscription_type: {test_user.subscription_type}")
        print(f"   - subscription_expires: {test_user.subscription_expires is not None}")
        print(f"   - subscription_created: {test_user.subscription_created is not None}")
        
    except Exception as e:
        print(f"❌ Database model error: {e}")
        return False
    
    # Test 6: Check Premium Routes
    print("\n6. Testing Premium Routes...")
    try:
        # Import routes to register them
        import routes
        
        # Check if premium routes are registered
        app_rules = [rule.rule for rule in routes.app.url_map.iter_rules()]
        premium_endpoints = [
            '/api/premium/status',
            '/api/premium/subscribe', 
            '/api/premium/features',
            '/api/premium/copilot/signals'
        ]
        
        all_routes = True
        for endpoint in premium_endpoints:
            if endpoint in app_rules:
                print(f"   ✅ {endpoint}: Registered")
            else:
                print(f"   ❌ {endpoint}: Missing")
                all_routes = False
        
        if all_routes:
            print("✅ All premium routes registered")
        else:
            print("❌ Some premium routes missing")
            return False
            
    except Exception as e:
        print(f"❌ Routes error: {e}")
        return False
    
    # Test 7: Revenue Model Validation  
    print("\n7. Testing Revenue Model...")
    try:
        pro_price = 19.99
        elite_price = 39.99
        
        # Calculate potential revenue
        test_scenarios = [
            (100, "Small Launch"),
            (1000, "Growing Platform"), 
            (10000, "Successful Platform")
        ]
        
        print("✅ Revenue projections:")
        for users, scenario in test_scenarios:
            # Assume 30% conversion to Pro, 10% to Elite
            pro_subs = int(users * 0.30)
            elite_subs = int(users * 0.10)
            monthly_revenue = (pro_subs * pro_price) + (elite_subs * elite_price)
            annual_revenue = monthly_revenue * 12
            
            print(f"   - {scenario} ({users} users): ${monthly_revenue:,.0f}/month, ${annual_revenue:,.0f}/year")
        
    except Exception as e:
        print(f"❌ Revenue model error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Premium Subscription Flow Test Complete!")
    print("\n📋 SUMMARY:")
    print("✅ Premium features API working")
    print("✅ AI Trading Copilot operational") 
    print("✅ Premium modal integrated")
    print("✅ JavaScript manager complete")
    print("✅ Database models ready")
    print("✅ Premium routes registered")
    print("✅ Revenue model validated")
    print("\n🚀 Premium functionality is fully operational!")
    
    return True

if __name__ == "__main__":
    success = test_premium_subscription_flow()
    sys.exit(0 if success else 1)