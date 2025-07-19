#!/usr/bin/env python3
"""
Test premium functionality and UI display
"""

import requests
import time

def test_premium_functionality():
    """Test that premium features display properly after subscription"""
    base_url = "http://localhost:5000"
    
    print("🔄 Testing Premium Functionality...")
    print("=" * 60)
    
    # Test 1: Check premium status API
    print("1. Testing Premium Status API...")
    try:
        response = requests.get(f"{base_url}/api/premium/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Premium status API working")
            print(f"   - Is Premium: {status.get('is_premium', False)}")
            print(f"   - Plan: {status.get('plan', 'free')}")
            print(f"   - Copilot Active: {status.get('copilot_active', False)}")
        else:
            print(f"❌ Premium status API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Premium status API error: {e}")
        return False
    
    # Test 2: Check copilot signals API
    print("\n2. Testing Copilot Signals API...")
    try:
        response = requests.get(f"{base_url}/api/premium/copilot/signals?limit=3", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Copilot signals API working")
            print(f"   - Signals returned: {data.get('count', 0)}")
            if data.get('signals'):
                for signal in data['signals'][:2]:
                    print(f"   - {signal['symbol']}: {signal['signal_type']} ({signal['confidence']*100:.0f}%)")
        elif response.status_code == 403:
            print("✅ Copilot signals API properly protected (403 for non-premium)")
        else:
            print(f"❌ Copilot signals API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Copilot signals API error: {e}")
    
    # Test 3: Verify JavaScript files are correct
    print("\n3. Testing JavaScript Implementation...")
    try:
        with open('static/js/premium.js', 'r') as f:
            content = f.read()
        
        # Check for proper field mapping
        if 'is_premium' in content:
            print("✅ JavaScript uses correct API field (is_premium)")
        else:
            print("❌ JavaScript may be using wrong field (isPremium vs is_premium)")
        
        # Check for debug logging
        if 'console.log' in content and 'Premium status received' in content:
            print("✅ Debug logging added for troubleshooting")
        else:
            print("❌ Debug logging missing")
        
        # Check for AI Copilot widget functions
        if 'showAICopilotWidget' in content and 'hideAICopilotWidget' in content:
            print("✅ AI Copilot widget functions present")
        else:
            print("❌ AI Copilot widget functions missing")
        
    except Exception as e:
        print(f"❌ JavaScript check error: {e}")
        return False
    
    # Test 4: Verify HTML template has copilot widget
    print("\n4. Testing HTML Template...")
    try:
        with open('templates/chatgpt_style_search.html', 'r') as f:
            content = f.read()
        
        if 'ai-copilot-widget' in content:
            print("✅ AI Copilot widget present in template")
        else:
            print("❌ AI Copilot widget missing from template")
            return False
        
        if 'notification-area' in content:
            print("✅ Notification area present in template")
        else:
            print("❌ Notification area missing from template")
            return False
        
    except Exception as e:
        print(f"❌ Template check error: {e}")
        return False
    
    # Test 5: Check CSS files exist
    print("\n5. Testing CSS Files...")
    try:
        with open('static/css/premium_features.css', 'r') as f:
            content = f.read()
        
        if '.ai-copilot-widget' in content:
            print("✅ AI Copilot widget styles present")
        else:
            print("❌ AI Copilot widget styles missing")
            return False
        
        if '.notification' in content:
            print("✅ Notification styles present")
        else:
            print("❌ Notification styles missing")
            return False
        
    except Exception as e:
        print(f"❌ CSS check error: {e}")
        return False
    
    # Test 6: Verify premium modal exists
    print("\n6. Testing Premium Modal...")
    try:
        with open('templates/premium_modal.html', 'r') as f:
            content = f.read()
        
        if 'premiumModal' in content:
            print("✅ Premium modal template exists")
        else:
            print("❌ Premium modal template missing")
            return False
        
        if 'Subscribe to' in content:
            print("✅ Subscription options present")
        else:
            print("❌ Subscription options missing")
        
    except Exception as e:
        print(f"❌ Premium modal check error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Premium Functionality Test Complete!")
    print("\n📋 WHAT SHOULD HAPPEN AFTER SUBSCRIPTION:")
    print("1. User clicks subscription plan in modal")
    print("2. Modal closes and beautiful success overlay appears")
    print("3. AI Copilot widget becomes visible on main interface")
    print("4. Widget shows live trading signals from AI")
    print("5. Upgrade button changes to 'Premium Active'")
    print("6. User stays on main interface (no redirects)")
    
    print("\n🔧 DEBUGGING STEPS:")
    print("1. Open browser dev tools (F12)")
    print("2. Subscribe to any plan")
    print("3. Watch console logs for 'Premium status received'")
    print("4. Look for AI Copilot widget appearing below search")
    print("5. Check if upgrade button changes color/text")
    
    return True

if __name__ == "__main__":
    success = test_premium_functionality()
    if success:
        print("\n✨ Ready for premium subscription testing!")
        print("💡 Subscribe and watch console logs to see what's happening")
    else:
        print("\n❌ Issues found - need fixes")