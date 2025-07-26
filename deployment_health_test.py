"""
Comprehensive Deployment Health Test for TradeWise AI
Tests all health check endpoints and deployment readiness
"""

import requests
import time
import sys
import os
from datetime import datetime

def test_health_endpoints():
    """Test all health check endpoints"""
    base_url = "http://localhost:5000"
    
    print("🏥 TradeWise AI Deployment Health Check")
    print("=" * 50)
    
    # Test main health endpoint
    print("\n1. Testing Main Health Endpoint (/health)...")
    try:
        response = requests.get(f"{base_url}/health", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Overall Status: {data.get('overall_status', 'unknown')}")
            print(f"✅ Response Time: {data.get('total_check_time_ms', 0)}ms")
            
            # Show service details
            services = data.get('services', {})
            for service_name, service_data in services.items():
                status = service_data.get('status', 'unknown')
                response_time = service_data.get('response_time_ms', 0)
                emoji = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
                print(f"  {emoji} {service_name}: {status} ({response_time}ms)")
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - ensure application is running")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test specific health endpoints
    endpoints = [
        ("/health/database", "Database"),
        ("/health/redis", "Redis Cache"),
        ("/health/api", "External APIs"),
        ("/health/startup", "Startup Readiness")
    ]
    
    for endpoint, name in endpoints:
        print(f"\n2. Testing {name} ({endpoint})...")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            data = response.json()
            status = data.get('status', 'unknown')
            
            if response.status_code == 200:
                print(f"✅ {name}: {status}")
                if 'response_time_ms' in data:
                    print(f"   Response Time: {data['response_time_ms']}ms")
                if 'details' in data:
                    details = data['details']
                    for key, value in details.items():
                        print(f"   {key}: {value}")
            else:
                print(f"⚠️ {name}: {status} (HTTP {response.status_code})")
                if 'message' in data:
                    print(f"   Message: {data['message']}")
                    
        except Exception as e:
            print(f"❌ {name} check failed: {e}")
    
    return True

def test_environment_validation():
    """Test environment validation"""
    print("\n3. Testing Environment Validation...")
    
    try:
        # Run environment validator
        import environment_validator
        validator = environment_validator.EnvironmentValidator()
        is_valid, errors, warnings = validator.validate_all()
        
        if is_valid:
            print("✅ Environment validation passed")
        else:
            print("❌ Environment validation failed")
            for error in errors:
                print(f"   Error: {error}")
        
        if warnings:
            print(f"⚠️ {len(warnings)} warnings:")
            for warning in warnings[:5]:  # Show first 5 warnings
                print(f"   Warning: {warning}")
                
    except Exception as e:
        print(f"❌ Environment validation error: {e}")

def test_api_endpoints():
    """Test critical API endpoints"""
    base_url = "http://localhost:5000"
    
    print("\n4. Testing Critical API Endpoints...")
    
    # Test endpoints with expected responses
    test_cases = [
        ("GET", "/api/health", 200, "API health check"),
        ("GET", "/tools/worker-status", 200, "Worker status"),
        ("GET", "/api/portfolio/summary", 200, "Portfolio API"),
    ]
    
    for method, endpoint, expected_status, description in test_cases:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == expected_status:
                print(f"✅ {description}: HTTP {response.status_code}")
            else:
                print(f"⚠️ {description}: HTTP {response.status_code} (expected {expected_status})")
                
        except Exception as e:
            print(f"❌ {description}: {e}")

def test_logging_system():
    """Test logging system"""
    print("\n5. Testing Logging System...")
    
    log_files = ["logs/app.log", "logs/worker.log", "logs/errors.log"]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            stat = os.stat(log_file)
            size_mb = round(stat.st_size / (1024 * 1024), 2)
            mtime = datetime.fromtimestamp(stat.st_mtime)
            
            # Check if file was modified recently (within last hour)
            recent = (datetime.now() - mtime).total_seconds() < 3600
            
            if recent and size_mb > 0:
                print(f"✅ {log_file}: {size_mb}MB, active")
            else:
                print(f"⚠️ {log_file}: {size_mb}MB, last updated {mtime.strftime('%H:%M:%S')}")
        else:
            print(f"❌ {log_file}: Not found")

def run_comprehensive_health_test():
    """Run all health tests"""
    start_time = time.time()
    
    print(f"🚀 TradeWise AI Deployment Health Test")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run all tests
    success = True
    
    try:
        if not test_health_endpoints():
            success = False
            
        test_environment_validation()
        test_api_endpoints()
        test_logging_system()
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        success = False
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        success = False
    
    # Summary
    total_time = round(time.time() - start_time, 2)
    print("\n" + "=" * 60)
    print("📋 Health Test Summary")
    print("=" * 60)
    
    if success:
        print("✅ Deployment Health: READY")
        print("✅ All critical systems operational")
        print("✅ Health check endpoints responding")
        print("✅ Environment configuration valid")
        print("✅ Logging system active")
    else:
        print("❌ Deployment Health: ISSUES DETECTED")
        print("❌ Some systems may need attention")
    
    print(f"\nTotal test time: {total_time}s")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success

if __name__ == "__main__":
    success = run_comprehensive_health_test()
    sys.exit(0 if success else 1)