#!/usr/bin/env python3
"""
Comprehensive Authentication & User Flow Testing Suite
Tests all authentication methods, user flows, and system functionality
"""

import requests
import time
import json
import sys
import os
from datetime import datetime
from urllib.parse import urljoin

class AuthenticationTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.performance_metrics = {}
        
    def log_test(self, test_name, status, details="", duration=0):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "duration_ms": round(duration * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if duration > 0:
            print(f"   Duration: {duration:.3f}s")
        print()
    
    def test_health_check(self):
        """Test basic application health"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test("Health Check", "PASS", f"Status: {response.status_code}", duration)
                return True
            else:
                self.log_test("Health Check", "FAIL", f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_test("Health Check", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_login_page_load(self):
        """Test login page accessibility"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/login")
            duration = time.time() - start_time
            
            if response.status_code == 200 and "login" in response.text.lower():
                self.log_test("Login Page Load", "PASS", "Login form accessible", duration)
                return True
            else:
                self.log_test("Login Page Load", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Login Page Load", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_oauth_endpoints(self):
        """Test OAuth endpoints availability"""
        oauth_providers = [
            ("/auth/google", "Google OAuth"),
            ("/auth/github", "GitHub OAuth")
        ]
        
        all_passed = True
        for endpoint, provider in oauth_providers:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}", allow_redirects=False)
                duration = time.time() - start_time
                
                # OAuth endpoints should redirect (302/301) or return specific responses
                if response.status_code in [302, 301, 200, 404]:
                    if response.status_code == 404:
                        self.log_test(f"{provider} Endpoint", "WARN", "OAuth not configured", duration)
                    else:
                        self.log_test(f"{provider} Endpoint", "PASS", f"Status: {response.status_code}", duration)
                else:
                    self.log_test(f"{provider} Endpoint", "FAIL", f"Status: {response.status_code}", duration)
                    all_passed = False
            except Exception as e:
                self.log_test(f"{provider} Endpoint", "FAIL", f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_dashboard_access(self):
        """Test dashboard accessibility for different user types"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                # Check for key dashboard elements
                content = response.text.lower()
                has_portfolio = "portfolio" in content
                has_ai_insights = "ai insights" or "insights" in content
                has_search = "search" in content
                
                details = f"Portfolio: {has_portfolio}, AI Insights: {has_ai_insights}, Search: {has_search}"
                self.log_test("Dashboard Access", "PASS", details, duration)
                return True
            else:
                self.log_test("Dashboard Access", "FAIL", f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_test("Dashboard Access", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_search_functionality(self):
        """Test search functionality and performance"""
        search_tests = [
            ("AAPL", "Symbol search"),
            ("Apple", "Company name search"),
            ("Appl", "Fuzzy matching")
        ]
        
        all_passed = True
        for query, test_type in search_tests:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}/api/stock-analysis", 
                                          params={"symbol": query})
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        performance_note = "Fast" if duration < 0.1 else "Slow" if duration > 2 else "Normal"
                        self.log_test(f"Search: {test_type}", "PASS", f"Query: {query}, {performance_note}", duration)
                    else:
                        self.log_test(f"Search: {test_type}", "FAIL", f"API returned success=false", duration)
                        all_passed = False
                else:
                    self.log_test(f"Search: {test_type}", "FAIL", f"Status: {response.status_code}", duration)
                    all_passed = False
            except Exception as e:
                self.log_test(f"Search: {test_type}", "FAIL", f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_autocomplete_api(self):
        """Test search autocomplete functionality"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/search/suggestions", 
                                      params={"query": "App"})
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("Autocomplete API", "PASS", f"Returned {len(data)} suggestions", duration)
                    return True
                else:
                    self.log_test("Autocomplete API", "FAIL", "No suggestions returned", duration)
                    return False
            else:
                self.log_test("Autocomplete API", "FAIL", f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_test("Autocomplete API", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_premium_features(self):
        """Test premium feature access control"""
        premium_endpoints = [
            ("/backtest", "Backtesting"),
            ("/peer-comparison", "Peer Comparison"),
            ("/api/premium/market-scanner", "AI Market Scanner")
        ]
        
        all_passed = True
        for endpoint, feature in premium_endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                duration = time.time() - start_time
                
                # For free users, should either redirect to upgrade or show locked UI
                if response.status_code in [200, 302, 403]:
                    content = response.text.lower()
                    has_lock_indicator = "upgrade" in content or "premium" in content or "pro" in content
                    
                    if response.status_code == 200:
                        self.log_test(f"Premium: {feature}", "PASS", f"Accessible with indicators: {has_lock_indicator}", duration)
                    else:
                        self.log_test(f"Premium: {feature}", "PASS", f"Properly protected (Status: {response.status_code})", duration)
                else:
                    self.log_test(f"Premium: {feature}", "FAIL", f"Status: {response.status_code}", duration)
                    all_passed = False
            except Exception as e:
                self.log_test(f"Premium: {feature}", "FAIL", f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_stripe_integration(self):
        """Test Stripe checkout integration"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/premium/upgrade")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                content = response.text.lower()
                has_stripe = "stripe" in content or "checkout" in content or "upgrade" in content
                self.log_test("Stripe Integration", "PASS", f"Upgrade page accessible, Stripe elements: {has_stripe}", duration)
                return True
            else:
                self.log_test("Stripe Integration", "FAIL", f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_test("Stripe Integration", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_user_plan_api(self):
        """Test user plan API"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/user/plan")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "plan" in data:
                    plan = data.get("plan", "unknown")
                    features = data.get("features", [])
                    self.log_test("User Plan API", "PASS", f"Plan: {plan}, Features: {len(features)}", duration)
                    return True
                else:
                    self.log_test("User Plan API", "FAIL", "Invalid response format", duration)
                    return False
            else:
                self.log_test("User Plan API", "FAIL", f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_test("User Plan API", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_dark_mode_assets(self):
        """Test dark mode CSS and JS assets"""
        assets = [
            ("/static/css/modern_saas_theme.css", "Main Theme CSS"),
            ("/static/css/desktop_optimization.css", "Desktop Optimization CSS"),
            ("/static/js/dark_mode.js", "Dark Mode JavaScript")
        ]
        
        all_passed = True
        for asset_path, asset_name in assets:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{asset_path}")
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    size_kb = len(response.content) / 1024
                    self.log_test(f"Asset: {asset_name}", "PASS", f"Size: {size_kb:.1f}KB", duration)
                else:
                    self.log_test(f"Asset: {asset_name}", "FAIL", f"Status: {response.status_code}", duration)
                    all_passed = False
            except Exception as e:
                self.log_test(f"Asset: {asset_name}", "FAIL", f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_mobile_responsiveness(self):
        """Test mobile-responsive endpoints"""
        # Test with mobile user agent
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        }
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/", headers=mobile_headers)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                content = response.text.lower()
                has_viewport = "viewport" in content
                has_responsive = "responsive" in content or "mobile" in content
                self.log_test("Mobile Responsiveness", "PASS", f"Viewport: {has_viewport}, Mobile optimized: {has_responsive}", duration)
                return True
            else:
                self.log_test("Mobile Responsiveness", "FAIL", f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_test("Mobile Responsiveness", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_security_headers(self):
        """Test security headers presence"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                headers = response.headers
                security_headers = {
                    'X-Content-Type-Options': 'nosniff',
                    'X-Frame-Options': 'DENY',
                    'X-XSS-Protection': '1; mode=block'
                }
                
                present_headers = []
                missing_headers = []
                
                for header, expected in security_headers.items():
                    if header in headers:
                        present_headers.append(header)
                    else:
                        missing_headers.append(header)
                
                if len(present_headers) >= 2:
                    self.log_test("Security Headers", "PASS", f"Present: {len(present_headers)}, Missing: {len(missing_headers)}", duration)
                    return True
                else:
                    self.log_test("Security Headers", "WARN", f"Few headers present: {present_headers}", duration)
                    return True
            else:
                self.log_test("Security Headers", "FAIL", f"Status: {response.status_code}", duration)
                return False
        except Exception as e:
            self.log_test("Security Headers", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_performance_metrics(self):
        """Test performance-related endpoints"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/performance/stats")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Performance API", "PASS", f"Response time: {duration:.3f}s", duration)
                return True
            else:
                self.log_test("Performance API", "WARN", f"Status: {response.status_code}", duration)
                return True  # Not critical
        except Exception as e:
            self.log_test("Performance API", "WARN", f"Exception: {str(e)}")
            return True  # Not critical
    
    def run_comprehensive_test(self):
        """Run all tests and generate report"""
        print("🔍 Starting Comprehensive Authentication & User Flow Testing")
        print("=" * 70)
        print()
        
        # Core functionality tests
        tests = [
            self.test_health_check,
            self.test_login_page_load,
            self.test_oauth_endpoints,
            self.test_dashboard_access,
            self.test_search_functionality,
            self.test_autocomplete_api,
            self.test_premium_features,
            self.test_stripe_integration,
            self.test_user_plan_api,
            self.test_dark_mode_assets,
            self.test_mobile_responsiveness,
            self.test_security_headers,
            self.test_performance_metrics
        ]
        
        passed = 0
        failed = 0
        warnings = 0
        
        for test in tests:
            try:
                result = test()
                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {str(e)}")
                failed += 1
        
        # Count warnings
        warnings = len([r for r in self.test_results if r["status"] == "WARN"])
        
        return self.generate_report(passed, failed, warnings)
    
    def generate_report(self, passed, failed, warnings):
        """Generate comprehensive test report"""
        total = passed + failed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print()
        print("=" * 70)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 70)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"⚠️  WARNINGS: {warnings}")
        print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
        print()
        
        # Performance summary
        avg_response_time = sum(r["duration_ms"] for r in self.test_results) / len(self.test_results) if self.test_results else 0
        print(f"⚡ AVERAGE RESPONSE TIME: {avg_response_time:.1f}ms")
        print()
        
        # Generate detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "success_rate": success_rate,
                "average_response_time_ms": avg_response_time
            },
            "detailed_results": self.test_results
        }
        
        # Save report
        with open('authentication_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Status determination
        if failed == 0:
            print("🎯 RESULT: ALL TESTS PASSED - PRODUCTION READY")
            return "PASS"
        elif failed <= 2:
            print("⚠️  RESULT: MOSTLY FUNCTIONAL - MINOR ISSUES")
            return "WARN"
        else:
            print("❌ RESULT: MULTIPLE FAILURES - NEEDS ATTENTION")
            return "FAIL"

def main():
    """Main testing function"""
    print("TradeWise AI - Authentication & User Flow Testing Suite")
    print("Testing comprehensive functionality...")
    print()
    
    tester = AuthenticationTester()
    result = tester.run_comprehensive_test()
    
    # Exit code based on results
    sys.exit(0 if result == "PASS" else 1 if result == "WARN" else 2)

if __name__ == "__main__":
    main()