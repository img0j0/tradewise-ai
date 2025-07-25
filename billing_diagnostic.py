"""
Billing System Diagnostic Tool
Identifies and fixes issues with the billing integration
"""

import sys
import traceback
from app import app, db

def test_billing_imports():
    """Test all billing-related imports"""
    print("Testing billing system imports...")
    
    try:
        from models import User, PlanConfiguration, SubscriptionHistory
        print("✅ Models imported successfully")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    try:
        from enhanced_stripe_billing import billing_manager
        print("✅ Stripe billing manager imported")
    except Exception as e:
        print(f"❌ Stripe billing manager import failed: {e}")
        return False
    
    try:
        from comprehensive_billing_routes import billing_bp
        print("✅ Billing routes imported")
    except Exception as e:
        print(f"❌ Billing routes import failed: {e}")
        return False
    
    return True

def test_database_models():
    """Test database model creation"""
    print("\nTesting database models...")
    
    with app.app_context():
        try:
            # Test basic model queries
            user_count = User.query.count()
            print(f"✅ User model working - {user_count} users in database")
            
            # Test if plan configuration table exists
            from models import PlanConfiguration
            plan_count = PlanConfiguration.query.count()
            print(f"✅ PlanConfiguration model working - {plan_count} plans configured")
            
            return True
        except Exception as e:
            print(f"❌ Database model test failed: {e}")
            traceback.print_exc()
            return False

def test_billing_manager():
    """Test billing manager initialization"""
    print("\nTesting billing manager...")
    
    try:
        from enhanced_stripe_billing import billing_manager
        
        # Test plan configurations
        plans = billing_manager.plan_configs
        print(f"✅ Billing manager has {len(plans)} plan configurations")
        
        for plan_name, config in plans.items():
            print(f"   - {plan_name}: {config.get('display_name', 'Unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Billing manager test failed: {e}")
        traceback.print_exc()
        return False

def initialize_plan_configs():
    """Initialize plan configurations in database"""
    print("\nInitializing plan configurations...")
    
    with app.app_context():
        try:
            from models import PlanConfiguration
            from enhanced_stripe_billing import billing_manager
            
            # Initialize plan configurations
            billing_manager.initialize_plan_configurations()
            
            # Verify they were created
            plans = PlanConfiguration.query.all()
            print(f"✅ Created {len(plans)} plan configurations")
            
            for plan in plans:
                print(f"   - {plan.plan_name}: ${plan.monthly_price}/month")
            
            return True
        except Exception as e:
            print(f"❌ Plan configuration initialization failed: {e}")
            traceback.print_exc()
            return False

def test_api_endpoints():
    """Test API endpoints manually"""
    print("\nTesting API endpoints...")
    
    with app.test_client() as client:
        try:
            # Test plans API
            response = client.get('/billing/api/plans')
            print(f"Plans API status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                if data and data.get('success'):
                    print(f"✅ Plans API working - {len(data['plans'])} plans returned")
                else:
                    print(f"❌ Plans API returned invalid data: {data}")
            else:
                print(f"❌ Plans API failed with status {response.status_code}")
                print(f"Response: {response.get_data(as_text=True)[:200]}...")
            
            return response.status_code == 200
        except Exception as e:
            print(f"❌ API endpoint test failed: {e}")
            traceback.print_exc()
            return False

def run_diagnostics():
    """Run complete diagnostic suite"""
    print("🔍 Running TradeWise AI Billing System Diagnostics")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_billing_imports():
        all_passed = False
    
    # Test database
    if not test_database_models():
        all_passed = False
    
    # Test billing manager
    if not test_billing_manager():
        all_passed = False
    
    # Initialize configurations
    if not initialize_plan_configs():
        all_passed = False
    
    # Test API endpoints
    if not test_api_endpoints():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All diagnostics passed! Billing system is ready.")
    else:
        print("❌ Some diagnostics failed. Check errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)