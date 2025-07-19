#!/usr/bin/env python3
"""
AI Team Visibility Test - Debug the AI team member widget visibility
"""

import requests
import time

def test_ai_team_visibility():
    """Test if AI team elements are properly loaded in the app"""
    
    base_url = "http://localhost:5000"
    
    try:
        # Test 1: Check if app is running
        print("🔍 Testing AI Team Member Visibility...")
        print("=" * 50)
        
        response = requests.get(base_url)
        if response.status_code != 200:
            print(f"❌ App not running (status: {response.status_code})")
            return False
        
        print("✅ App is running")
        
        # Test 2: Check if HTML contains AI team elements
        content = response.text
        
        # Check for AI team launcher
        if 'ai-team-launcher' in content:
            print("✅ AI team launcher element found in HTML")
        else:
            print("❌ AI team launcher element missing from HTML")
            return False
            
        # Check for AI team widget
        if 'ai-team-widget' in content:
            print("✅ AI team widget element found in HTML")
        else:
            print("❌ AI team widget element missing from HTML")
            return False
        
        # Check for AI team JavaScript
        if 'ai_team_chat.js' in content:
            print("✅ AI team JavaScript included")
        else:
            print("❌ AI team JavaScript missing")
            return False
        
        # Test 3: Check if API endpoints are working
        print("\n🔍 Testing AI Team API Endpoints...")
        
        # Test team members endpoint (public)
        try:
            api_response = requests.get(f"{base_url}/api/ai-team/members")
            if api_response.status_code == 200:
                data = api_response.json()
                if data.get('success') and data.get('members'):
                    print(f"✅ AI team members API working ({len(data['members'])} members)")
                    for member in data['members']:
                        print(f"   - {member['name']} ({member['role']})")
                else:
                    print("❌ AI team members API returned invalid data")
                    return False
            else:
                print(f"❌ AI team members API failed (status: {api_response.status_code})")
                return False
        except Exception as e:
            print(f"❌ AI team members API error: {e}")
            return False
        
        # Test 4: Check specific HTML elements
        print("\n🔍 Checking HTML Structure...")
        
        # Check for Font Awesome
        if 'font-awesome' in content or 'fas fa-users' in content:
            print("✅ Font Awesome icons included")
        else:
            print("⚠️  Font Awesome icons may not be loaded")
        
        # Check for CSS styling
        if 'position: fixed' in content and 'bottom:' in content:
            print("✅ Fixed positioning CSS found")
        else:
            print("⚠️  Fixed positioning CSS may be missing")
        
        print("\n✅ AI Team system appears to be properly integrated!")
        print("\n💡 If you still can't see the AI team launcher:")
        print("   1. Check browser console for JavaScript errors")
        print("   2. Look for a purple circular button in bottom-right corner")
        print("   3. Try refreshing the page")
        print("   4. Check if any other floating elements are overlapping")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to app - make sure it's running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_ai_team_visibility()
    exit(0 if success else 1)