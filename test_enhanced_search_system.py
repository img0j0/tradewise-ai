#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Search System
Tests fuzzy matching, autocomplete, accuracy, and performance
"""

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

class SearchSystemTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = {
            'accuracy_tests': [],
            'performance_tests': [],
            'fuzzy_matching_tests': [],
            'autocomplete_tests': [],
            'error_handling_tests': []
        }
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Enhanced Search System Test Suite")
        print("=" * 60)
        
        # Test Categories
        self.test_exact_symbol_matching()
        self.test_company_name_search()
        self.test_fuzzy_matching()
        self.test_partial_matching()
        self.test_autocomplete_performance()
        self.test_trending_stocks()
        self.test_error_handling()
        self.test_concurrent_requests()
        
        # Generate report
        self.generate_report()
    
    def test_exact_symbol_matching(self):
        """Test exact symbol matching accuracy"""
        print("\n📊 Testing Exact Symbol Matching")
        
        exact_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'META', 'AMZN', 'NFLX']
        
        for symbol in exact_symbols:
            try:
                response = requests.get(f"{self.base_url}/api/search/autocomplete?q={symbol}")
                data = response.json()
                
                if data.get('success') and data.get('suggestions'):
                    first_result = data['suggestions'][0]
                    is_exact = first_result.get('symbol') == symbol
                    match_type = first_result.get('match_type', 'unknown')
                    
                    self.results['accuracy_tests'].append({
                        'query': symbol,
                        'expected': symbol,
                        'got': first_result.get('symbol'),
                        'exact_match': is_exact,
                        'match_type': match_type,
                        'response_time': data.get('execution_time_ms', 0)
                    })
                    
                    status = "✅" if is_exact else "❌"
                    print(f"  {status} {symbol}: {first_result.get('symbol')} [{match_type}] ({data.get('execution_time_ms', 0)}ms)")
                else:
                    print(f"  ❌ {symbol}: No results returned")
                    self.results['accuracy_tests'].append({
                        'query': symbol,
                        'expected': symbol,
                        'got': None,
                        'exact_match': False,
                        'match_type': 'no_result',
                        'response_time': 0
                    })
                    
            except Exception as e:
                print(f"  ❌ {symbol}: Error - {e}")
    
    def test_company_name_search(self):
        """Test company name to symbol conversion"""
        print("\n🏢 Testing Company Name Search")
        
        company_tests = [
            ('Apple', 'AAPL'),
            ('Microsoft', 'MSFT'),
            ('Tesla', 'TSLA'),
            ('Amazon', 'AMZN'),
            ('Google', 'GOOGL'),
            ('Meta', 'META'),
            ('Netflix', 'NFLX'),
            ('Nvidia', 'NVDA')
        ]
        
        for company_name, expected_symbol in company_tests:
            try:
                response = requests.get(f"{self.base_url}/api/search/autocomplete?q={company_name}")
                data = response.json()
                
                if data.get('success') and data.get('suggestions'):
                    # Check if expected symbol is in top 3 results
                    found_symbols = [s.get('symbol') for s in data['suggestions'][:3]]
                    is_found = expected_symbol in found_symbols
                    
                    first_result = data['suggestions'][0]
                    match_type = first_result.get('match_type', 'unknown')
                    
                    self.results['accuracy_tests'].append({
                        'query': company_name,
                        'expected': expected_symbol,
                        'got': found_symbols[0] if found_symbols else None,
                        'found_in_top3': is_found,
                        'match_type': match_type,
                        'response_time': data.get('execution_time_ms', 0)
                    })
                    
                    status = "✅" if is_found else "❌"
                    print(f"  {status} {company_name} → {expected_symbol}: Found in {found_symbols} [{match_type}]")
                else:
                    print(f"  ❌ {company_name}: No results returned")
                    
            except Exception as e:
                print(f"  ❌ {company_name}: Error - {e}")
    
    def test_fuzzy_matching(self):
        """Test fuzzy matching for typos and partial inputs"""
        print("\n🔍 Testing Fuzzy Matching")
        
        fuzzy_tests = [
            ('Appl', 'AAPL'),    # Missing letter
            ('Microsft', 'MSFT'), # Typo
            ('Teslas', 'TSLA'),   # Extra letter
            ('Gogle', 'GOOGL'),   # Missing letter
            ('Amazn', 'AMZN'),    # Missing letter
            ('Netflx', 'NFLX'),   # Missing letter
        ]
        
        for fuzzy_query, expected_symbol in fuzzy_tests:
            try:
                response = requests.get(f"{self.base_url}/api/search/autocomplete?q={fuzzy_query}")
                data = response.json()
                
                if data.get('success') and data.get('suggestions'):
                    found_symbols = [s.get('symbol') for s in data['suggestions'][:3]]
                    is_found = expected_symbol in found_symbols
                    
                    first_result = data['suggestions'][0]
                    match_score = first_result.get('match_score', 0)
                    
                    self.results['fuzzy_matching_tests'].append({
                        'query': fuzzy_query,
                        'expected': expected_symbol,
                        'found_in_results': is_found,
                        'match_score': match_score,
                        'response_time': data.get('execution_time_ms', 0)
                    })
                    
                    status = "✅" if is_found else "❌"
                    print(f"  {status} {fuzzy_query} → {expected_symbol}: Score {match_score} ({data.get('execution_time_ms', 0)}ms)")
                else:
                    print(f"  ❌ {fuzzy_query}: No results returned")
                    
            except Exception as e:
                print(f"  ❌ {fuzzy_query}: Error - {e}")
    
    def test_partial_matching(self):
        """Test partial input matching"""
        print("\n📝 Testing Partial Matching")
        
        partial_tests = [
            ('App', ['AAPL']),           # Should find Apple
            ('Mic', ['MSFT']),           # Should find Microsoft  
            ('Tes', ['TSLA']),           # Should find Tesla
            ('Goo', ['GOOGL', 'GOOG']), # Should find Google
            ('Net', ['NFLX']),           # Should find Netflix
        ]
        
        for partial_query, expected_symbols in partial_tests:
            try:
                response = requests.get(f"{self.base_url}/api/search/autocomplete?q={partial_query}")
                data = response.json()
                
                if data.get('success') and data.get('suggestions'):
                    found_symbols = [s.get('symbol') for s in data['suggestions'][:5]]
                    matches_found = [sym for sym in expected_symbols if sym in found_symbols]
                    
                    success_rate = len(matches_found) / len(expected_symbols)
                    
                    self.results['fuzzy_matching_tests'].append({
                        'query': partial_query,
                        'expected': expected_symbols,
                        'found': matches_found,
                        'success_rate': success_rate,
                        'response_time': data.get('execution_time_ms', 0)
                    })
                    
                    status = "✅" if success_rate >= 0.5 else "❌"
                    print(f"  {status} {partial_query}: Found {matches_found} (Success: {success_rate:.1%})")
                else:
                    print(f"  ❌ {partial_query}: No results returned")
                    
            except Exception as e:
                print(f"  ❌ {partial_query}: Error - {e}")
    
    def test_autocomplete_performance(self):
        """Test autocomplete response times"""
        print("\n⚡ Testing Autocomplete Performance")
        
        performance_queries = ['A', 'AA', 'AAP', 'AAPL', 'Apple', 'App', 'Te', 'Tesla']
        response_times = []
        
        for query in performance_queries:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/api/search/autocomplete?q={query}")
                end_time = time.time()
                
                request_time = (end_time - start_time) * 1000  # Convert to ms
                
                data = response.json()
                api_time = data.get('execution_time_ms', 0)
                
                response_times.append(request_time)
                
                self.results['performance_tests'].append({
                    'query': query,
                    'request_time_ms': request_time,
                    'api_time_ms': api_time,
                    'success': data.get('success', False),
                    'result_count': len(data.get('suggestions', []))
                })
                
                status = "✅" if request_time < 500 else "⚠️" if request_time < 1000 else "❌"
                print(f"  {status} {query}: {request_time:.1f}ms (API: {api_time}ms) - {len(data.get('suggestions', []))} results")
                
            except Exception as e:
                print(f"  ❌ {query}: Error - {e}")
        
        if response_times:
            avg_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            max_time = max(response_times)
            
            print(f"\n📊 Performance Summary:")
            print(f"  Average: {avg_time:.1f}ms")
            print(f"  Median: {median_time:.1f}ms") 
            print(f"  Max: {max_time:.1f}ms")
    
    def test_trending_stocks(self):
        """Test trending stocks endpoint"""
        print("\n📈 Testing Trending Stocks")
        
        try:
            response = requests.get(f"{self.base_url}/api/search/trending")
            data = response.json()
            
            if data.get('success') and data.get('trending_stocks'):
                trending_count = len(data['trending_stocks'])
                
                print(f"  ✅ Trending endpoint working: {trending_count} stocks")
                
                # Check data quality
                for i, stock in enumerate(data['trending_stocks'][:5]):
                    symbol = stock.get('symbol', 'N/A')
                    name = stock.get('name', 'N/A')
                    trend = stock.get('trend', 'unknown')
                    ai_score = stock.get('ai_score', 0)
                    
                    print(f"    {i+1}. {symbol} - {name} [Trend: {trend}, AI: {ai_score}]")
                
                self.results['autocomplete_tests'].append({
                    'endpoint': 'trending',
                    'success': True,
                    'count': trending_count
                })
            else:
                print("  ❌ Trending endpoint failed")
                
        except Exception as e:
            print(f"  ❌ Trending stocks: Error - {e}")
    
    def test_error_handling(self):
        """Test error handling for edge cases"""
        print("\n🛡️ Testing Error Handling")
        
        error_tests = [
            ('', 'Empty query'),
            ('   ', 'Whitespace only'),
            ('INVALIDSTOCK123', 'Invalid stock symbol'),
            ('🚀💎🌙', 'Special characters'),
            ('x' * 100, 'Very long query')
        ]
        
        for query, description in error_tests:
            try:
                response = requests.get(f"{self.base_url}/api/search/autocomplete?q={query}")
                data = response.json()
                
                # Should either succeed with results or fail gracefully
                success = data.get('success', False)
                suggestions = data.get('suggestions', [])
                
                self.results['error_handling_tests'].append({
                    'query': query,
                    'description': description,
                    'success': success,
                    'result_count': len(suggestions),
                    'graceful': response.status_code == 200
                })
                
                status = "✅" if response.status_code == 200 else "❌"
                print(f"  {status} {description}: {len(suggestions)} results")
                
            except Exception as e:
                print(f"  ❌ {description}: Error - {e}")
    
    def test_concurrent_requests(self):
        """Test system under concurrent load"""
        print("\n🔄 Testing Concurrent Requests")
        
        queries = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'META'] * 4  # 20 requests
        response_times = []
        successful_requests = 0
        
        def make_request(query):
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/api/search/autocomplete?q={query}")
                end_time = time.time()
                
                request_time = (end_time - start_time) * 1000
                data = response.json()
                
                return {
                    'query': query,
                    'success': data.get('success', False),
                    'response_time': request_time,
                    'result_count': len(data.get('suggestions', []))
                }
            except Exception as e:
                return {
                    'query': query,
                    'success': False,
                    'error': str(e),
                    'response_time': 0
                }
        
        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, query) for query in queries]
            
            for future in as_completed(futures):
                result = future.result()
                if result['success']:
                    successful_requests += 1
                    response_times.append(result['response_time'])
        
        success_rate = successful_requests / len(queries)
        
        if response_times:
            avg_time = statistics.mean(response_times)
            print(f"  ✅ Concurrent test: {success_rate:.1%} success rate")
            print(f"  Average response time: {avg_time:.1f}ms")
        else:
            print("  ❌ Concurrent test failed")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📋 ENHANCED SEARCH SYSTEM TEST REPORT")
        print("=" * 60)
        
        # Accuracy Report
        accuracy_tests = self.results['accuracy_tests']
        if accuracy_tests:
            exact_matches = sum(1 for t in accuracy_tests if t.get('exact_match', False))
            accuracy_rate = exact_matches / len(accuracy_tests)
            
            avg_response_time = statistics.mean([t['response_time'] for t in accuracy_tests if t['response_time'] > 0])
            
            print(f"\n🎯 ACCURACY RESULTS:")
            print(f"  Exact Symbol Matches: {exact_matches}/{len(accuracy_tests)} ({accuracy_rate:.1%})")
            print(f"  Average Response Time: {avg_response_time:.1f}ms")
        
        # Fuzzy Matching Report
        fuzzy_tests = self.results['fuzzy_matching_tests']
        if fuzzy_tests:
            successful_fuzzy = sum(1 for t in fuzzy_tests if t.get('found_in_results', False) or t.get('success_rate', 0) > 0.5)
            fuzzy_rate = successful_fuzzy / len(fuzzy_tests)
            
            print(f"\n🔍 FUZZY MATCHING RESULTS:")
            print(f"  Successful Fuzzy Matches: {successful_fuzzy}/{len(fuzzy_tests)} ({fuzzy_rate:.1%})")
        
        # Performance Report
        performance_tests = self.results['performance_tests']
        if performance_tests:
            fast_requests = sum(1 for t in performance_tests if t['request_time_ms'] < 500)
            performance_rate = fast_requests / len(performance_tests)
            
            print(f"\n⚡ PERFORMANCE RESULTS:")
            print(f"  Fast Requests (<500ms): {fast_requests}/{len(performance_tests)} ({performance_rate:.1%})")
        
        # Overall Grade
        overall_scores = []
        if accuracy_tests:
            overall_scores.append(exact_matches / len(accuracy_tests))
        if fuzzy_tests:
            overall_scores.append(successful_fuzzy / len(fuzzy_tests))
        if performance_tests:
            overall_scores.append(fast_requests / len(performance_tests))
        
        if overall_scores:
            overall_grade = statistics.mean(overall_scores)
            
            print(f"\n🏆 OVERALL SYSTEM GRADE:")
            if overall_grade >= 0.95:
                print(f"  EXCELLENT: {overall_grade:.1%} ✅✅✅")
            elif overall_grade >= 0.85:
                print(f"  VERY GOOD: {overall_grade:.1%} ✅✅")
            elif overall_grade >= 0.75:
                print(f"  GOOD: {overall_grade:.1%} ✅")
            else:
                print(f"  NEEDS IMPROVEMENT: {overall_grade:.1%} ⚠️")
        
        print("\n" + "=" * 60)
        print("✅ Test suite completed successfully!")

if __name__ == "__main__":
    tester = SearchSystemTester()
    tester.run_all_tests()