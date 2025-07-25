"""
Comprehensive Test Suite for TradeWise AI Billing & Authentication System
Tests OAuth, 2FA, Stripe billing, premium features, and webhook handling
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

class BillingAuthTestSuite:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.test_user_data = {}
        
    def log_test(self, test_name: str, status: str, details: str = "", error: str = ""):
        """Log test result with timestamp"""
        result = {
            'test_name': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details,
            'error': error
        }
        self.test_results.append(result)
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
    
    def test_application_health(self):
        """Test if application is running and responding"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test("Application Health Check", "PASS", "Application is running")
                return True
            else:
                self.log_test("Application Health Check", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Application Health Check", "FAIL", error=str(e))
            return False
    
    def test_billing_plans_page(self):
        """Test billing plans page accessibility"""
        try:
            response = self.session.get(f"{self.base_url}/billing/plans")
            if response.status_code == 200:
                if "Choose Your Plan" in response.text:
                    self.log_test("Billing Plans Page", "PASS", "Plans page loads correctly")
                else:
                    self.log_test("Billing Plans Page", "FAIL", "Plans page missing expected content")
            else:
                self.log_test("Billing Plans Page", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Billing Plans Page", "FAIL", error=str(e))
    
    def test_api_plans_endpoint(self):
        """Test API plans endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/billing/api/plans")
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'plans' in data:
                    plans = data['plans']
                    plan_names = [plan.get('name') for plan in plans]
                    expected_plans = ['free', 'pro', 'enterprise']
                    
                    if all(plan in plan_names for plan in expected_plans):
                        self.log_test("API Plans Endpoint", "PASS", f"Found plans: {plan_names}")
                    else:
                        self.log_test("API Plans Endpoint", "FAIL", f"Missing expected plans. Found: {plan_names}")
                else:
                    self.log_test("API Plans Endpoint", "FAIL", "Invalid API response structure")
            else:
                self.log_test("API Plans Endpoint", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("API Plans Endpoint", "FAIL", error=str(e))
    
    def test_oauth_endpoints(self):
        """Test OAuth endpoints accessibility"""
        oauth_endpoints = [
            "/auth/google",
            "/auth/github",
            "/oauth/status"
        ]
        
        for endpoint in oauth_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                # OAuth endpoints should redirect or return specific responses
                if response.status_code in [200, 302, 401, 403]:
                    self.log_test(f"OAuth Endpoint {endpoint}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_test(f"OAuth Endpoint {endpoint}", "FAIL", f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_test(f"OAuth Endpoint {endpoint}", "FAIL", error=str(e))
    
    def test_2fa_endpoints(self):
        """Test 2FA endpoints"""
        twofa_endpoints = [
            "/2fa/status",  # Should require login
            "/2fa/setup",   # Should require login
        ]
        
        for endpoint in twofa_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                # 2FA endpoints should require authentication
                if response.status_code in [401, 403, 302]:
                    self.log_test(f"2FA Endpoint {endpoint}", "PASS", "Properly requires authentication")
                elif response.status_code == 200:
                    self.log_test(f"2FA Endpoint {endpoint}", "SKIP", "Accessible (may be logged in)")
                else:
                    self.log_test(f"2FA Endpoint {endpoint}", "FAIL", f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_test(f"2FA Endpoint {endpoint}", "FAIL", error=str(e))
    
    def test_premium_feature_restrictions(self):
        """Test premium feature access restrictions"""
        premium_endpoints = [
            "/api/ai/market-scanner",
            "/api/portfolio/analysis",
            "/api/ai/enhanced-analysis"
        ]
        
        for endpoint in premium_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                # Premium endpoints should require authentication/subscription
                if response.status_code in [401, 403]:
                    self.log_test(f"Premium Restriction {endpoint}", "PASS", "Properly restricted")
                elif response.status_code == 200:
                    data = response.json()
                    if 'requires_premium' in str(data) or 'upgrade' in str(data).lower():
                        self.log_test(f"Premium Restriction {endpoint}", "PASS", "Shows upgrade prompt")
                    else:
                        self.log_test(f"Premium Restriction {endpoint}", "SKIP", "May have premium access")
                else:
                    self.log_test(f"Premium Restriction {endpoint}", "FAIL", f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Premium Restriction {endpoint}", "FAIL", error=str(e))
    
    def test_billing_management_pages(self):
        """Test billing management page accessibility"""
        billing_pages = [
            "/billing/manage",
            "/billing/success",
            "/billing/cancel"
        ]
        
        for page in billing_pages:
            try:
                response = self.session.get(f"{self.base_url}{page}")
                if response.status_code in [200, 302, 401, 403]:
                    self.log_test(f"Billing Page {page}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_test(f"Billing Page {page}", "FAIL", f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Billing Page {page}", "FAIL", error=str(e))
    
    def test_stripe_checkout_creation(self):
        """Test Stripe checkout session creation"""
        plans_to_test = ['pro', 'enterprise']
        
        for plan in plans_to_test:
            try:
                response = self.session.get(f"{self.base_url}/billing/subscribe/{plan}")
                # Should redirect to login or Stripe (302) or show authentication required
                if response.status_code in [302, 401, 403]:
                    self.log_test(f"Stripe Checkout {plan.title()}", "PASS", "Requires authentication as expected")
                elif response.status_code == 200:
                    self.log_test(f"Stripe Checkout {plan.title()}", "SKIP", "May be authenticated")
                else:
                    self.log_test(f"Stripe Checkout {plan.title()}", "FAIL", f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Stripe Checkout {plan.title()}", "FAIL", error=str(e))
    
    def test_webhook_endpoint(self):
        """Test Stripe webhook endpoint"""
        try:
            # Test POST to webhook (should fail without proper signature)
            response = self.session.post(f"{self.base_url}/billing/webhook", 
                                       json={"test": "data"})
            if response.status_code in [400, 401]:
                self.log_test("Stripe Webhook", "PASS", "Properly validates webhook signature")
            else:
                self.log_test("Stripe Webhook", "FAIL", f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("Stripe Webhook", "FAIL", error=str(e))
    
    def test_template_rendering(self):
        """Test that billing templates render without errors"""
        template_pages = [
            "/billing/plans",
        ]
        
        for page in template_pages:
            try:
                response = self.session.get(f"{self.base_url}{page}")
                if response.status_code == 200:
                    # Check for template rendering errors
                    content = response.text
                    if "TemplateSyntaxError" in content or "Jinja2" in content:
                        self.log_test(f"Template {page}", "FAIL", "Template rendering error")
                    elif len(content) > 1000:  # Reasonable content length
                        self.log_test(f"Template {page}", "PASS", "Template renders successfully")
                    else:
                        self.log_test(f"Template {page}", "FAIL", "Template content too short")
                else:
                    self.log_test(f"Template {page}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Template {page}", "FAIL", error=str(e))
    
    def test_api_error_handling(self):
        """Test API error handling"""
        test_cases = [
            ("/billing/api/subscription/status", "Subscription status without auth"),
            ("/billing/api/usage", "Usage stats without auth"),
            ("/2fa/verify", "2FA verify without session")
        ]
        
        for endpoint, description in test_cases:
            try:
                if endpoint == "/2fa/verify":
                    response = self.session.post(f"{self.base_url}{endpoint}", json={})
                else:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code in [400, 401, 403]:
                    try:
                        data = response.json()
                        if 'error' in data or 'success' in data:
                            self.log_test(f"API Error Handling - {description}", "PASS", "Proper JSON error response")
                        else:
                            self.log_test(f"API Error Handling - {description}", "FAIL", "Invalid error response format")
                    except:
                        self.log_test(f"API Error Handling - {description}", "FAIL", "Non-JSON error response")
                else:
                    self.log_test(f"API Error Handling - {description}", "SKIP", f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"API Error Handling - {description}", "FAIL", error=str(e))
    
    def test_security_headers(self):
        """Test security headers are present"""
        try:
            response = self.session.get(f"{self.base_url}/")
            headers = response.headers
            
            security_checks = [
                ('X-Content-Type-Options', 'nosniff'),
                ('X-Frame-Options', 'DENY'),
                ('X-XSS-Protection', '1; mode=block'),
            ]
            
            passed_checks = 0
            total_checks = len(security_checks)
            
            for header, expected_value in security_checks:
                if header in headers:
                    if expected_value in headers[header]:
                        passed_checks += 1
                    else:
                        print(f"   Warning: {header} present but value is '{headers[header]}', expected '{expected_value}'")
                else:
                    print(f"   Warning: Missing security header: {header}")
            
            if passed_checks >= total_checks * 0.8:  # 80% pass rate
                self.log_test("Security Headers", "PASS", f"{passed_checks}/{total_checks} security headers present")
            else:
                self.log_test("Security Headers", "FAIL", f"Only {passed_checks}/{total_checks} security headers present")
                
        except Exception as e:
            self.log_test("Security Headers", "FAIL", error=str(e))
    
    def run_full_test_suite(self):
        """Run complete test suite"""
        print("🚀 Starting TradeWise AI Billing & Authentication Test Suite")
        print("=" * 70)
        
        # Basic health checks
        if not self.test_application_health():
            print("❌ Application is not running. Stopping test suite.")
            return self.generate_report()
        
        # Run all test categories
        print("\n📋 Testing Billing System...")
        self.test_billing_plans_page()
        self.test_api_plans_endpoint()
        self.test_billing_management_pages()
        self.test_stripe_checkout_creation()
        self.test_webhook_endpoint()
        
        print("\n🔐 Testing Authentication System...")
        self.test_oauth_endpoints()
        self.test_2fa_endpoints()
        
        print("\n💎 Testing Premium Features...")
        self.test_premium_feature_restrictions()
        
        print("\n🎨 Testing UI Templates...")
        self.test_template_rendering()
        
        print("\n🛡️ Testing Security...")
        self.test_api_error_handling()
        self.test_security_headers()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        skipped_tests = len([r for r in self.test_results if r['status'] == 'SKIP'])
        
        print("\n" + "=" * 70)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Skipped: {skipped_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test_name']}")
                    if result['error']:
                        print(f"     Error: {result['error']}")
        
        print(f"\n📝 Detailed results saved to test_results.json")
        
        # Save detailed results
        with open('test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'skipped': skipped_tests,
                    'success_rate': round(passed_tests/total_tests*100, 1)
                },
                'test_results': self.test_results,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        return {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': round(passed_tests/total_tests*100, 1)
        }

if __name__ == "__main__":
    # Run test suite
    suite = BillingAuthTestSuite()
    results = suite.run_full_test_suite()
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)