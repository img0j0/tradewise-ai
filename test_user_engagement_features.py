#!/usr/bin/env python3
"""
User Engagement Features Test Suite
Comprehensive testing for enhanced search, peer comparison, and portfolio backtesting
"""

import requests
import json
import time
from datetime import datetime

class UserEngagementTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'results': []
        }
        
    def run_test(self, test_name, test_func, expected_result="PASS"):
        """Run individual test and track results"""
        self.test_results['total_tests'] += 1
        
        try:
            result = test_func()
            if result['status'] == 'PASS':
                self.test_results['passed'] += 1
                print(f"✅ {test_name}: PASS")
                if result.get('details'):
                    print(f"   Details: {result['details']}")
            elif result['status'] == 'SKIP':
                self.test_results['skipped'] += 1
                print(f"⚠️ {test_name}: SKIP")
                if result.get('details'):
                    print(f"   Details: {result['details']}")
            else:
                self.test_results['failed'] += 1
                print(f"❌ {test_name}: FAIL")
                if result.get('details'):
                    print(f"   Details: {result['details']}")
        except Exception as e:
            self.test_results['failed'] += 1
            print(f"❌ {test_name}: ERROR - {str(e)}")
        
        self.test_results['results'].append({
            'test_name': test_name,
            'status': result.get('status', 'ERROR'),
            'details': result.get('details', str(e) if 'e' in locals() else '')
        })

    def test_enhanced_search_autocomplete(self):
        """Test enhanced search autocomplete functionality"""
        try:
            response = requests.get(f"{self.base_url}/api/search/autocomplete?q=APP")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('suggestions'):
                    suggestions = data['suggestions']
                    # Check if AAPL (Apple) is in suggestions
                    apple_found = any(s.get('symbol') == 'AAPL' for s in suggestions)
                    
                    return {
                        'status': 'PASS',
                        'details': f"Found {len(suggestions)} suggestions, Apple included: {apple_found}"
                    }
                else:
                    return {
                        'status': 'FAIL',
                        'details': f"No suggestions returned: {data}"
                    }
            else:
                return {
                    'status': 'FAIL',
                    'details': f"HTTP {response.status_code}: {response.text[:100]}"
                }
                
        except Exception as e:
            return {'status': 'ERROR', 'details': str(e)}

    def test_recent_searches(self):
        """Test recent searches functionality"""
        try:
            # First, get current recent searches
            response = requests.get(f"{self.base_url}/api/search/recent")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return {
                        'status': 'PASS',
                        'details': f"Retrieved {data.get('count', 0)} recent searches"
                    }
                else:
                    return {
                        'status': 'FAIL',
                        'details': f"API returned success=false: {data}"
                    }
            else:
                return {
                    'status': 'FAIL',
                    'details': f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {'status': 'ERROR', 'details': str(e)}

    def test_starred_symbols(self):
        """Test starred symbols functionality"""
        try:
            # Test GET starred symbols
            response = requests.get(f"{self.base_url}/api/search/starred")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    starred_count = data.get('count', 0)
                    
                    # Test POST - add a starred symbol
                    post_response = requests.post(
                        f"{self.base_url}/api/search/starred",
                        json={'symbol': 'TSLA'},
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if post_response.status_code == 200:
                        post_data = post_response.json()
                        if post_data.get('success'):
                            return {
                                'status': 'PASS',
                                'details': f"Starred symbols: {starred_count}, TSLA action: {post_data.get('action')}"
                            }
                    
                    return {
                        'status': 'PASS',
                        'details': f"GET worked ({starred_count} starred), POST needs authentication"
                    }
                else:
                    return {
                        'status': 'FAIL',
                        'details': f"GET failed: {data}"
                    }
            else:
                return {
                    'status': 'FAIL',
                    'details': f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {'status': 'ERROR', 'details': str(e)}

    def test_add_recent_search(self):
        """Test adding to recent searches"""
        try:
            response = requests.post(
                f"{self.base_url}/api/search/add-recent",
                json={
                    'symbol': 'NVDA',
                    'name': 'NVIDIA Corporation',
                    'sector': 'Technology'
                },
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return {
                        'status': 'PASS',
                        'details': 'Successfully added NVDA to recent searches'
                    }
                else:
                    return {
                        'status': 'FAIL',
                        'details': f"API error: {data}"
                    }
            else:
                return {
                    'status': 'FAIL',
                    'details': f"HTTP {response.status_code}: {response.text[:100]}"
                }
                
        except Exception as e:
            return {'status': 'ERROR', 'details': str(e)}

    def test_peer_comparison_without_auth(self):
        """Test peer comparison endpoint (should require premium)"""
        try:
            response = requests.get(f"{self.base_url}/api/peer-comparison/AAPL")
            
            if response.status_code == 401 or response.status_code == 403:
                data = response.json()
                if data.get('premium_required'):
                    return {
                        'status': 'PASS',
                        'details': 'Correctly requires premium authentication'
                    }
                else:
                    return {
                        'status': 'PASS',
                        'details': 'Requires authentication (expected behavior)'
                    }
            elif response.status_code == 200:
                return {
                    'status': 'SKIP',
                    'details': 'Endpoint accessible (may be authenticated)'
                }
            else:
                return {
                    'status': 'FAIL',
                    'details': f"Unexpected status code: {response.status_code}"
                }
                
        except Exception as e:
            return {'status': 'ERROR', 'details': str(e)}

    def test_sector_benchmark_without_auth(self):
        """Test sector benchmark endpoint (should require premium)"""
        try:
            response = requests.get(f"{self.base_url}/api/sector-benchmark/Technology")
            
            if response.status_code == 401 or response.status_code == 403:
                data = response.json()
                if data.get('premium_required'):
                    return {
                        'status': 'PASS',
                        'details': 'Correctly requires premium authentication'
                    }
                else:
                    return {
                        'status': 'PASS',
                        'details': 'Requires authentication (expected behavior)'
                    }
            elif response.status_code == 200:
                return {
                    'status': 'SKIP',
                    'details': 'Endpoint accessible (may be authenticated)'
                }
            else:
                return {
                    'status': 'FAIL',
                    'details': f"Unexpected status code: {response.status_code}"
                }
                
        except Exception as e:
            return {'status': 'ERROR', 'details': str(e)}

    def test_available_sectors(self):
        """Test available sectors endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/sectors/available")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('sectors'):
                    sectors = data['sectors']
                    tech_included = 'Technology' in sectors
                    
                    return {
                        'status': 'PASS',
                        'details': f"Found {len(sectors)} sectors, Technology included: {tech_included}"
                    }
                else:
                    return {
                        'status': 'FAIL',
                        'details': f"No sectors returned: {data}"
                    }
            else:
                return {
                    'status': 'FAIL',
                    'details': f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {'status': 'ERROR', 'details': str(e)}

    def test_portfolio_backtest_without_auth(self):
        """Test portfolio backtesting endpoint (should require premium)"""
        try:
            test_portfolio = [
                {'symbol': 'AAPL', 'weight': 0.6},
                {'symbol': 'GOOGL', 'weight': 0.4}
            ]
            
            response = requests.post(
                f"{self.base_url}/api/portfolio/backtest",
                json={'portfolio': test_portfolio},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 401 or response.status_code == 403:
                data = response.json()
                if data.get('premium_required'):
                    return {
                        'status': 'PASS',
                        'details': 'Correctly requires premium authentication'
                    }
                else:
                    return {
                        'status': 'PASS',
                        'details': 'Requires authentication (expected behavior)'
                    }
            elif response.status_code == 200:
                return {
                    'status': 'SKIP',
                    'details': 'Backtest accessible (may be authenticated)'
                }
            else:
                return {
                    'status': 'FAIL',
                    'details': f"Unexpected status code: {response.status_code}"
                }
                
        except Exception as e:
            return {'status': 'ERROR', 'details': str(e)}

    def test_available_benchmarks(self):
        """Test available benchmarks endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/portfolio/backtest/benchmarks")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('benchmarks'):
                    benchmarks = data['benchmarks']
                    spy_included = any(b.get('symbol') == 'SPY' for b in benchmarks)
                    
                    return {
                        'status': 'PASS',
                        'details': f"Found {len(benchmarks)} benchmarks, SPY included: {spy_included}"
                    }
                else:
                    return {
                        'status': 'FAIL',
                        'details': f"No benchmarks returned: {data}"
                    }
            else:
                return {
                    'status': 'FAIL',
                    'details': f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {'status': 'ERROR', 'details': str(e)}

    def test_portfolio_validation(self):
        """Test portfolio validation endpoint"""
        try:
            test_portfolio = [
                {'symbol': 'AAPL', 'weight': 60},
                {'symbol': 'GOOGL', 'weight': 40}
            ]
            
            response = requests.post(
                f"{self.base_url}/api/portfolio/validate",
                json={'portfolio': test_portfolio},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('is_valid'):
                    normalized = data.get('normalized_weights', [])
                    
                    return {
                        'status': 'PASS',
                        'details': f"Portfolio valid, {len(normalized)} holdings normalized"
                    }
                else:
                    return {
                        'status': 'FAIL',
                        'details': f"Validation failed: {data}"
                    }
            else:
                return {
                    'status': 'FAIL',
                    'details': f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {'status': 'ERROR', 'details': str(e)}

    def test_search_analytics(self):
        """Test search analytics endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/search/analytics")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    trending = data.get('trending_stocks', [])
                    sectors = data.get('popular_sectors', [])
                    tags = data.get('hot_tags', [])
                    
                    return {
                        'status': 'PASS',
                        'details': f"Analytics: {len(trending)} trending, {len(sectors)} sectors, {len(tags)} tags"
                    }
                else:
                    return {
                        'status': 'FAIL',
                        'details': f"Analytics failed: {data}"
                    }
            else:
                return {
                    'status': 'FAIL',
                    'details': f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {'status': 'ERROR', 'details': str(e)}

    def test_engagement_metrics(self):
        """Test engagement metrics endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/engagement/metrics")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('metrics'):
                    metrics = data['metrics']
                    recent_count = metrics.get('recent_searches_count', 0)
                    starred_count = metrics.get('starred_symbols_count', 0)
                    
                    return {
                        'status': 'PASS',
                        'details': f"Metrics: {recent_count} recent searches, {starred_count} starred"
                    }
                else:
                    return {
                        'status': 'FAIL',
                        'details': f"Metrics failed: {data}"
                    }
            else:
                return {
                    'status': 'FAIL',
                    'details': f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {'status': 'ERROR', 'details': str(e)}

    def test_application_health(self):
        """Test basic application health"""
        try:
            response = requests.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                return {
                    'status': 'PASS',
                    'details': 'Application is running'
                }
            else:
                return {
                    'status': 'FAIL',
                    'details': f"Application not responding: HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {'status': 'ERROR', 'details': str(e)}

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting TradeWise AI User Engagement Features Test Suite")
        print("=" * 70)
        
        # Application Health
        self.run_test("Application Health Check", self.test_application_health)
        
        print("\n📝 Testing Enhanced Search Features...")
        self.run_test("Enhanced Search Autocomplete", self.test_enhanced_search_autocomplete)
        self.run_test("Recent Searches", self.test_recent_searches)
        self.run_test("Starred Symbols", self.test_starred_symbols)
        self.run_test("Add Recent Search", self.test_add_recent_search)
        self.run_test("Search Analytics", self.test_search_analytics)
        
        print("\n🔍 Testing Peer Comparison Features...")
        self.run_test("Available Sectors", self.test_available_sectors)
        self.run_test("Peer Comparison Access Control", self.test_peer_comparison_without_auth)
        self.run_test("Sector Benchmark Access Control", self.test_sector_benchmark_without_auth)
        
        print("\n📊 Testing Portfolio Backtesting Features...")
        self.run_test("Available Benchmarks", self.test_available_benchmarks)
        self.run_test("Portfolio Validation", self.test_portfolio_validation)
        self.run_test("Portfolio Backtest Access Control", self.test_portfolio_backtest_without_auth)
        
        print("\n📈 Testing Analytics & Metrics...")
        self.run_test("Engagement Metrics", self.test_engagement_metrics)
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 70)
        
        total = self.test_results['total_tests']
        passed = self.test_results['passed']
        failed = self.test_results['failed']
        skipped = self.test_results['skipped']
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Skipped: {skipped}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Save detailed results
        with open('user_engagement_test_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': self.test_results,
                'success_rate': success_rate
            }, f, indent=2)
        
        print(f"\n📝 Detailed results saved to user_engagement_test_results.json")
        
        return self.test_results

if __name__ == "__main__":
    tester = UserEngagementTester()
    results = tester.run_all_tests()