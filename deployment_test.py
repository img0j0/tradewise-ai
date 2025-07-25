#!/usr/bin/env python3
"""
Post-deployment validation script for TradeWise AI
Tests all critical endpoints and functionality after Render deployment
"""

import requests
import json
import time
import sys
import os
from typing import Dict, List, Tuple
import concurrent.futures
from datetime import datetime

class DeploymentTester:
    """Comprehensive deployment testing suite"""
    
    def __init__(self, base_url: str = "https://tradewiseai.com"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TradeWise-AI-Deployment-Test/1.0'
        })
        self.results = []
        self.start_time = datetime.now()
    
    def log(self, message: str, test_name: str = "GENERAL", status: str = "INFO"):
        """Log test results with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status:8} | {test_name:25} | {message}")
        
        self.results.append({
            'timestamp': timestamp,
            'test_name': test_name,
            'status': status,
            'message': message
        })
    
    def test_health_check(self) -> bool:
        """Test basic health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log(f"✅ Health check passed - {data.get('database')}", 
                            "HEALTH_CHECK", "PASS")
                    return True
                else:
                    self.log(f"❌ Health check failed - Status: {data.get('status')}", 
                            "HEALTH_CHECK", "FAIL")
                    return False
            else:
                self.log(f"❌ Health endpoint returned {response.status_code}", 
                        "HEALTH_CHECK", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"❌ Health check error: {str(e)}", "HEALTH_CHECK", "ERROR")
            return False
    
    def test_ssl_certificate(self) -> bool:
        """Test SSL certificate validity"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            
            if response.url.startswith('https://'):
                self.log("✅ HTTPS redirect working", "SSL_CHECK", "PASS")
                return True
            else:
                self.log("❌ HTTPS redirect not working", "SSL_CHECK", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"❌ SSL check error: {str(e)}", "SSL_CHECK", "ERROR")
            return False
    
    def test_stock_analysis_cached(self) -> bool:
        """Test stock analysis with cached data"""
        try:
            # Test popular stock that should be pre-computed
            response = self.session.get(
                f"{self.base_url}/api/stock-analysis?symbol=AAPL", 
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('symbol') == 'AAPL':
                    price = data.get('current_price', 0)
                    self.log(f"✅ Stock analysis (AAPL) - Price: ${price:.2f}", 
                            "STOCK_ANALYSIS_CACHED", "PASS")
                    return True
                else:
                    self.log("❌ Stock analysis response invalid", 
                            "STOCK_ANALYSIS_CACHED", "FAIL")
                    return False
            else:
                self.log(f"❌ Stock analysis returned {response.status_code}", 
                        "STOCK_ANALYSIS_CACHED", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"❌ Stock analysis error: {str(e)}", 
                    "STOCK_ANALYSIS_CACHED", "ERROR")
            return False
    
    def test_stock_analysis_async(self) -> bool:
        """Test async stock analysis workflow"""
        try:
            # Request async analysis
            response = self.session.post(
                f"{self.base_url}/api/stock-analysis",
                json={"symbol": "TSLA", "async": True},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('async_mode') and data.get('task_id'):
                    task_id = data['task_id']
                    self.log(f"✅ Async task queued - ID: {task_id[:8]}...", 
                            "STOCK_ANALYSIS_ASYNC", "PASS")
                    
                    # Test status endpoint
                    status_url = f"{self.base_url}{data.get('status_url')}"
                    status_response = self.session.get(status_url, timeout=5)
                    
                    if status_response.status_code == 200:
                        self.log("✅ Task status endpoint working", 
                                "ASYNC_STATUS", "PASS")
                        return True
                    else:
                        self.log("❌ Task status endpoint failed", 
                                "ASYNC_STATUS", "FAIL")
                        return False
                else:
                    self.log("❌ Async response missing required fields", 
                            "STOCK_ANALYSIS_ASYNC", "FAIL")
                    return False
            else:
                self.log(f"❌ Async analysis returned {response.status_code}", 
                        "STOCK_ANALYSIS_ASYNC", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"❌ Async analysis error: {str(e)}", 
                    "STOCK_ANALYSIS_ASYNC", "ERROR")
            return False
    
    def test_market_overview(self) -> bool:
        """Test market overview endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/market/overview", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log("✅ Market overview endpoint working", 
                            "MARKET_OVERVIEW", "PASS")
                    return True
                else:
                    self.log("❌ Market overview response invalid", 
                            "MARKET_OVERVIEW", "FAIL")
                    return False
            else:
                self.log(f"❌ Market overview returned {response.status_code}", 
                        "MARKET_OVERVIEW", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"❌ Market overview error: {str(e)}", "MARKET_OVERVIEW", "ERROR")
            return False
    
    def test_performance_metrics(self) -> bool:
        """Test performance metrics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/performance/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('endpoint_stats'):
                    self.log("✅ Performance metrics available", 
                            "PERFORMANCE_METRICS", "PASS")
                    return True
                else:
                    self.log("❌ Performance metrics response invalid", 
                            "PERFORMANCE_METRICS", "FAIL")
                    return False
            else:
                self.log(f"❌ Performance metrics returned {response.status_code}", 
                        "PERFORMANCE_METRICS", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"❌ Performance metrics error: {str(e)}", 
                    "PERFORMANCE_METRICS", "ERROR")
            return False
    
    def test_prometheus_metrics(self) -> bool:
        """Test Prometheus metrics endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/metrics", timeout=10)
            
            if response.status_code == 200:
                content = response.text
                if 'flask_request_total' in content:
                    self.log("✅ Prometheus metrics exposed", 
                            "PROMETHEUS_METRICS", "PASS")
                    return True
                else:
                    self.log("❌ Prometheus metrics format invalid", 
                            "PROMETHEUS_METRICS", "FAIL")
                    return False
            else:
                self.log(f"❌ Prometheus metrics returned {response.status_code}", 
                        "PROMETHEUS_METRICS", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"❌ Prometheus metrics error: {str(e)}", 
                    "PROMETHEUS_METRICS", "ERROR")
            return False
    
    def test_premium_authentication(self) -> bool:
        """Test premium endpoint authentication"""
        try:
            # Test without authentication (should fail)
            response = self.session.get(
                f"{self.base_url}/api/premium/portfolio-optimizer", 
                timeout=10
            )
            
            if response.status_code in [401, 403]:
                self.log("✅ Premium authentication enforced", 
                        "PREMIUM_AUTH", "PASS")
                return True
            else:
                self.log(f"❌ Premium endpoint accessible without auth ({response.status_code})", 
                        "PREMIUM_AUTH", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"❌ Premium auth test error: {str(e)}", "PREMIUM_AUTH", "ERROR")
            return False
    
    def test_load_performance(self) -> bool:
        """Test basic load performance"""
        try:
            # Concurrent requests test
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for i in range(10):
                    future = executor.submit(
                        self.session.get, 
                        f"{self.base_url}/api/health", 
                        timeout=10
                    )
                    futures.append(future)
                
                # Wait for all requests to complete
                results = []
                for future in concurrent.futures.as_completed(futures):
                    try:
                        response = future.result()
                        results.append(response.status_code == 200)
                    except Exception:
                        results.append(False)
            
            end_time = time.time()
            duration = end_time - start_time
            success_rate = sum(results) / len(results) * 100
            
            if success_rate >= 90 and duration < 10:
                self.log(f"✅ Load test passed - {success_rate:.1f}% success in {duration:.2f}s", 
                        "LOAD_PERFORMANCE", "PASS")
                return True
            else:
                self.log(f"❌ Load test failed - {success_rate:.1f}% success in {duration:.2f}s", 
                        "LOAD_PERFORMANCE", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"❌ Load test error: {str(e)}", "LOAD_PERFORMANCE", "ERROR")
            return False
    
    def test_domain_routing(self) -> bool:
        """Test domain routing and redirects"""
        try:
            # Test www redirect
            www_response = self.session.get(f"https://www.tradewiseai.com", timeout=10)
            
            if www_response.url.startswith("https://tradewiseai.com"):
                self.log("✅ WWW redirect working", "DOMAIN_ROUTING", "PASS")
                return True
            else:
                self.log("❌ WWW redirect not working", "DOMAIN_ROUTING", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"❌ Domain routing error: {str(e)}", "DOMAIN_ROUTING", "ERROR")
            return False
    
    def run_all_tests(self) -> Dict:
        """Run all deployment tests"""
        self.log("Starting TradeWise AI deployment validation", "DEPLOYMENT_TEST", "START")
        self.log(f"Target URL: {self.base_url}", "DEPLOYMENT_TEST", "INFO")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("SSL Certificate", self.test_ssl_certificate),
            ("Domain Routing", self.test_domain_routing),
            ("Stock Analysis (Cached)", self.test_stock_analysis_cached),
            ("Stock Analysis (Async)", self.test_stock_analysis_async),
            ("Market Overview", self.test_market_overview),
            ("Performance Metrics", self.test_performance_metrics),
            ("Prometheus Metrics", self.test_prometheus_metrics),
            ("Premium Authentication", self.test_premium_authentication),
            ("Load Performance", self.test_load_performance),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log(f"❌ Test {test_name} crashed: {str(e)}", "TEST_RUNNER", "ERROR")
                failed += 1
        
        # Summary
        total_time = (datetime.now() - self.start_time).total_seconds()
        success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        
        self.log(f"Tests completed in {total_time:.2f}s", "DEPLOYMENT_TEST", "INFO")
        self.log(f"Results: {passed} passed, {failed} failed ({success_rate:.1f}% success)", 
                "DEPLOYMENT_TEST", "SUMMARY")
        
        if success_rate >= 90:
            self.log("🎉 DEPLOYMENT VALIDATION PASSED", "DEPLOYMENT_TEST", "SUCCESS")
        else:
            self.log("💥 DEPLOYMENT VALIDATION FAILED", "DEPLOYMENT_TEST", "FAILURE")
        
        return {
            'passed': passed,
            'failed': failed,
            'success_rate': success_rate,
            'total_time': total_time,
            'results': self.results
        }
    
    def generate_report(self) -> str:
        """Generate detailed test report"""
        report = []
        report.append("# TradeWise AI Deployment Test Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append(f"Target URL: {self.base_url}")
        report.append("")
        
        # Summary
        passed = len([r for r in self.results if r['status'] == 'PASS'])
        failed = len([r for r in self.results if r['status'] in ['FAIL', 'ERROR']])
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        report.append("## Summary")
        report.append(f"- **Total Tests**: {passed + failed}")
        report.append(f"- **Passed**: {passed}")
        report.append(f"- **Failed**: {failed}")
        report.append(f"- **Success Rate**: {(passed/(passed+failed)*100):.1f}%")
        report.append(f"- **Duration**: {total_time:.2f} seconds")
        report.append("")
        
        # Detailed Results
        report.append("## Detailed Results")
        for result in self.results:
            if result['status'] in ['PASS', 'FAIL', 'ERROR']:
                status_emoji = "✅" if result['status'] == 'PASS' else "❌"
                report.append(f"- {status_emoji} **{result['test_name']}**: {result['message']}")
        
        return "\n".join(report)

def main():
    """Main test runner"""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://tradewiseai.com"
    
    tester = DeploymentTester(base_url)
    results = tester.run_all_tests()
    
    # Generate and save report
    report = tester.generate_report()
    with open('deployment_test_report.md', 'w') as f:
        f.write(report)
    
    print("\n" + "="*80)
    print("📄 Full report saved to: deployment_test_report.md")
    
    # Exit with appropriate code
    sys.exit(0 if results['success_rate'] >= 90 else 1)

if __name__ == "__main__":
    main()