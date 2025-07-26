"""
Enhanced Error Handling Test Suite for TradeWise AI
Tests all error handling components and logging system
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from error_handler import TradeWiseError, ErrorHandler, setup_logging
from tools_error_wrapper import tool_error_handler, api_tool_handler, safe_json_response
import logging

# Initialize logging
logger = setup_logging()

@tool_error_handler("Test Tool", "validation")
def test_validation_error():
    """Test validation error handling"""
    raise ValueError("Invalid stock symbol format")

@api_tool_handler("Test API", "Yahoo Finance")
def test_api_timeout():
    """Test API timeout error handling"""
    import requests
    raise requests.exceptions.Timeout("API request timed out")

@api_tool_handler("Test API", "Yahoo Finance")
def test_api_rate_limit():
    """Test API rate limit error handling"""
    import requests
    response = requests.Response()
    response.status_code = 429
    error = requests.exceptions.HTTPError(response=response)
    raise error

def test_tradewise_error():
    """Test custom TradeWise error"""
    raise TradeWiseError('API_KEY_MISSING', 'Stripe API key not configured')

def test_successful_operation():
    """Test successful operation"""
    @tool_error_handler("Test Tool", "success")
    def success_func():
        return {"message": "Operation completed successfully", "data": [1, 2, 3]}
    
    return success_func()

def run_error_tests():
    """Run comprehensive error handling tests"""
    print("🧪 Testing TradeWise AI Error Handling System")
    print("=" * 50)
    
    # Test 1: Validation Error
    print("\n1. Testing Validation Error...")
    try:
        result = test_validation_error()
        print(f"✅ Validation error handled: {result['error']['message']}")
    except Exception as e:
        print(f"❌ Validation error test failed: {e}")
    
    # Test 2: API Timeout
    print("\n2. Testing API Timeout...")
    try:
        result = test_api_timeout()
        print(f"✅ API timeout handled: {result['error']['message']}")
    except Exception as e:
        print(f"❌ API timeout test failed: {e}")
    
    # Test 3: TradeWise Custom Error
    print("\n3. Testing Custom TradeWise Error...")
    try:
        test_tradewise_error()
    except TradeWiseError as e:
        response = e.get_error_response()
        print(f"✅ Custom error handled: {response['error']['message']}")
    except Exception as e:
        print(f"❌ Custom error test failed: {e}")
    
    # Test 4: Successful Operation
    print("\n4. Testing Successful Operation...")
    try:
        result = test_successful_operation()
        print(f"✅ Success case handled: {result['status']} - {result['data']}")
    except Exception as e:
        print(f"❌ Success test failed: {e}")
    
    # Test 5: JSON Response Safety
    print("\n5. Testing Safe JSON Response...")
    try:
        test_data = {
            'status': 'success',
            'data': {'symbol': 'AAPL', 'price': 150.25},
            'timestamp': '2025-07-26T01:48:00Z'
        }
        response, status_code = safe_json_response(test_data)
        print(f"✅ Safe JSON response: Status {status_code}")
    except Exception as e:
        print(f"❌ JSON response test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Error Handling System Test Complete")
    print("📝 Check logs/ directory for detailed error logs")

if __name__ == "__main__":
    run_error_tests()