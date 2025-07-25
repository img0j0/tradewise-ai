# TradeWise AI Deployment Test Report
Generated: 2025-07-25 20:00:55 UTC
Target URL: http://localhost:5000

## Summary
- **Total Tests**: 10
- **Passed**: 5
- **Failed**: 5
- **Success Rate**: 50.0%
- **Duration**: 7.04 seconds

## Detailed Results
- ✅ **HEALTH_CHECK**: ✅ Health check passed - connected
- ❌ **SSL_CHECK**: ❌ HTTPS redirect not working
- ❌ **DOMAIN_ROUTING**: ❌ Domain routing error: HTTPSConnectionPool(host='www.tradewiseai.com', port=443): Max retries exceeded with url: / (Caused by NameResolutionError("<urllib3.connection.HTTPSConnection object at 0x7f0165d742d0>: Failed to resolve 'www.tradewiseai.com' ([Errno -2] Name or service not known)"))
- ✅ **STOCK_ANALYSIS_CACHED**: ✅ Stock analysis (AAPL) - Price: $0.00
- ❌ **STOCK_ANALYSIS_ASYNC**: ❌ Async response missing required fields
- ✅ **MARKET_OVERVIEW**: ✅ Market overview endpoint working
- ❌ **PERFORMANCE_METRICS**: ❌ Performance metrics response invalid
- ✅ **PROMETHEUS_METRICS**: ✅ Prometheus metrics exposed
- ❌ **PREMIUM_AUTH**: ❌ Premium endpoint accessible without auth (404)
- ✅ **LOAD_PERFORMANCE**: ✅ Load test passed - 100.0% success in 0.60s